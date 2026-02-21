from __future__ import annotations

"""
Docker sandbox — secure, isolated code execution via subprocess.

Uses `docker run` through asyncio.create_subprocess_exec (NOT the Docker SDK,
NOT exec/eval). Each execution:
  1. Writes code + stdin to a temp directory
  2. Spawns `docker run` with strict security flags
  3. Captures stdout/stderr with a hard timeout
  4. Parses container exit code to determine verdict
  5. Container auto-removed via --rm

Security constraints:
  - network_mode=none (--network=none)
  - No Linux capabilities (--cap-drop ALL)
  - No privilege escalation (--security-opt no-new-privileges)
  - PID limit (--pids-limit 64)
  - Memory hard cap, no swap (--memory / --memory-swap)
  - CPU limit (--cpus)
  - Wall-clock timeout (asyncio.wait_for)
  - Container auto-removed after execution (--rm)
  - Concurrency semaphore prevents resource exhaustion
"""

import os
import time
import uuid
import asyncio
import tempfile
import logging
from dataclasses import dataclass

from backend.config import settings
from backend.execution.languages import get_language_config

logger = logging.getLogger(__name__)

# Exit code Docker uses when it kills a container for exceeding memory
DOCKER_OOM_EXIT_CODE = 137
# Exit code from `timeout` command when it kills the process
TIMEOUT_EXIT_CODE = 124

# ── Concurrency control ──────────────────────────────────────
# Limit parallel Docker containers to prevent host resource exhaustion.
# On a typical dev machine, 4 concurrent containers is safe.
# In production, tune this based on host RAM / CPU.
MAX_CONCURRENT_CONTAINERS = 4
_container_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONTAINERS)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Structured result
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class ExecutionResult:
    """Immutable result of a sandboxed code execution."""
    stdout: str
    stderr: str
    exit_code: int
    time_ms: int
    memory_kb: int
    timed_out: bool
    oom_killed: bool
    stage: str  # "compile", "run", or "unknown"

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and not self.oom_killed

    def to_dict(self) -> dict:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "time_ms": self.time_ms,
            "memory_kb": self.memory_kb,
            "timed_out": self.timed_out,
            "oom_killed": self.oom_killed,
            "stage": self.stage,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Sandbox class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Sandbox:
    """
    Subprocess-based Docker sandbox.
    Spawns `docker run` via asyncio.create_subprocess_exec — no Docker SDK,
    no exec(), no eval(). Pure process spawning with captured pipes.
    """

    async def execute(
        self,
        language: str,
        code: str,
        stdin_data: str,
        time_limit_ms: int | None = None,
        memory_limit_mb: int | None = None,
    ) -> ExecutionResult:
        """
        Execute user code inside a Docker container.

        Args:
            language:        One of 'python', 'cpp', 'java', 'javascript'
            code:            Source code string
            stdin_data:      Input to feed to the program via stdin
            time_limit_ms:   Max execution time in milliseconds (default: 2000)
            memory_limit_mb: Max memory in MB (default: from settings)

        Returns:
            ExecutionResult with stdout, stderr, exit code, timing, and verdict flags
        """
        exec_id = uuid.uuid4().hex[:8]
        config = get_language_config(language)

        # Default to 2-second timeout per the user requirement
        timeout_seconds = (time_limit_ms / 1000.0) if time_limit_ms else 2.0

        # Parse memory limit (supports "256m" or "256")
        mem_limit_str = settings.sandbox_memory_limit.rstrip("mM")
        try:
            mem_mb = memory_limit_mb or int(mem_limit_str)
        except ValueError:
            logger.warning(f"Invalid memory limit format: {settings.sandbox_memory_limit}, using 256MB")
            mem_mb = memory_limit_mb or 256

        # ── Ensure input ends with newline ─────────────────
        if stdin_data and not stdin_data.endswith("\n"):
            stdin_data += "\n"

        logger.info(
            f"[SANDBOX:{exec_id}] Starting: "
            f"lang={language}, input_len={len(stdin_data or '')}, "
            f"time_limit={time_limit_ms}ms, mem_limit={mem_mb}MB, "
            f"input_preview={repr((stdin_data or '')[:200])}"
        )

        # ── Acquire concurrency semaphore ─────────────────
        async with _container_semaphore:
            logger.debug(f"[SANDBOX:{exec_id}] Acquired semaphore slot")

            with tempfile.TemporaryDirectory(prefix=f"codearena_{exec_id}_") as tmpdir:
                # ── Write code file ───────────────────────────
                if language == "java":
                    filename = f"Solution{config.file_extension}"
                else:
                    filename = f"code{config.file_extension}"

                code_path = os.path.join(tmpdir, filename)
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)

                # ── Write stdin file ──────────────────────────
                stdin_path = os.path.join(tmpdir, "input.txt")
                with open(stdin_path, "w", encoding="utf-8") as f:
                    f.write(stdin_data or "")

                # ── Build shell commands ──────────────────────
                # Separate compile and run for proper error classification
                if config.needs_compilation:
                    # Step 1: Compile
                    compile_result = await self._run_compile(
                        exec_id, config, tmpdir, mem_mb, timeout_seconds
                    )
                    if compile_result is not None:
                        # Compilation failed — return compile error result
                        return compile_result

                    # Step 2: Run the compiled binary
                    inner_cmd = f"{config.run_cmd} < /sandbox/input.txt"
                else:
                    inner_cmd = f"{config.run_cmd} < /sandbox/input.txt"

                # ── Build docker run args ─────────────────────
                # Use UUID to guarantee unique container names (prevents collisions)
                container_name = f"codearena-{exec_id}"

                docker_args = [
                    "docker", "run",
                    "--name", container_name,

                    # ── Security ──────────────────────────────
                    "--network", "none",              # No network access
                    "--cap-drop", "ALL",              # Drop all Linux capabilities
                    "--security-opt", "no-new-privileges:true",

                    # ── Resource limits ───────────────────────
                    "--memory", f"{mem_mb}m",         # Hard memory limit
                    "--memory-swap", f"{mem_mb}m",    # No swap (swap = mem → 0 swap)
                    "--pids-limit", str(settings.sandbox_pids_limit),
                    "--cpus", "0.5",                  # Half a CPU core

                    # ── Filesystem ────────────────────────────
                    # /tmp writable WITHOUT noexec (JVM JIT needs exec)
                    "--tmpfs", "/tmp:size=64m,nosuid",
                    "-v", f"{tmpdir}:/sandbox:rw",    # Mount code directory

                    # ── Cleanup ───────────────────────────────
                    "--rm",                           # Auto-remove on exit

                    # ── Override entrypoint ────────────────────
                    "--entrypoint", "sh",

                    # ── Image + command ───────────────────────
                    config.image,
                    "-c", inner_cmd,
                ]

                # ── Execute ──────────────────────────────────
                result = await self._run_process(
                    exec_id, docker_args, container_name, timeout_seconds,
                    stage="run",
                )

                logger.info(
                    f"[SANDBOX:{exec_id}] Result: "
                    f"stage={result.stage}, exit_code={result.exit_code}, "
                    f"timed_out={result.timed_out}, oom_killed={result.oom_killed}, "
                    f"time_ms={result.time_ms}, "
                    f"stdout_len={len(result.stdout)}, "
                    f"stderr_len={len(result.stderr)}, "
                    f"stderr_preview={repr(result.stderr[:500])}"
                )

                return result

    async def _run_compile(
        self,
        exec_id: str,
        config,
        tmpdir: str,
        mem_mb: int,
        timeout_seconds: float,
    ) -> ExecutionResult | None:
        """
        Run compilation step separately. Returns ExecutionResult if compile
        failed, or None if compilation succeeded.
        """
        container_name = f"codearena-compile-{exec_id}"

        compile_cmd = f"cd /sandbox && {config.compile_cmd}"

        docker_args = [
            "docker", "run",
            "--name", container_name,

            # Security
            "--network", "none",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",

            # Resource limits
            "--memory", f"{mem_mb}m",
            "--memory-swap", f"{mem_mb}m",
            "--pids-limit", str(settings.sandbox_pids_limit),
            "--cpus", "0.5",

            # Filesystem
            "--tmpfs", "/tmp:size=64m,nosuid",
            "-v", f"{tmpdir}:/sandbox:rw",

            # Cleanup
            "--rm",

            # Override entrypoint
            "--entrypoint", "sh",

            # Image + command
            config.image,
            "-c", compile_cmd,
        ]

        # Compilation gets a generous timeout (settings.sandbox_compile_timeout)
        compile_timeout = settings.sandbox_compile_timeout

        result = await self._run_process(
            exec_id, docker_args, container_name, compile_timeout,
            stage="compile",
        )

        if result.exit_code != 0:
            logger.info(
                f"[SANDBOX:{exec_id}] Compilation FAILED: "
                f"exit_code={result.exit_code}, "
                f"stderr={repr(result.stderr[:500])}"
            )
            return result

        logger.info(f"[SANDBOX:{exec_id}] Compilation succeeded")
        return None  # Success — proceed to run

    async def _run_process(
        self,
        exec_id: str,
        docker_args: list[str],
        container_name: str,
        timeout_seconds: float,
        stage: str = "run",
    ) -> ExecutionResult:
        """
        Spawn `docker run` as an async subprocess, capture output,
        enforce timeout, and parse the result.
        """
        timed_out = False
        oom_killed = False
        stdout_bytes = b""
        stderr_bytes = b""
        exit_code = 1

        proc: asyncio.subprocess.Process | None = None

        try:
            # Log the full docker command for debugging
            logger.debug(
                f"[SANDBOX:{exec_id}] Docker cmd: {' '.join(docker_args)}"
            )

            # Spawn the docker run process
            proc = await asyncio.create_subprocess_exec(
                *docker_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Start timing AFTER the process is spawned (measure user code, not Docker overhead)
            start_time = time.monotonic()

            # Wait with hard timeout (+5s buffer for Docker startup overhead)
            docker_overhead_buffer = 5.0
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_seconds + docker_overhead_buffer,
                )
                exit_code = proc.returncode or 0
            except asyncio.TimeoutError:
                timed_out = True
                exit_code = -1
                logger.warning(
                    f"[SANDBOX:{exec_id}] Process timed out after "
                    f"{timeout_seconds + docker_overhead_buffer}s (stage={stage})"
                )

                # Kill the process tree
                try:
                    proc.kill()
                    await proc.wait()
                except ProcessLookupError:
                    pass

                # Force-kill the Docker container (--rm will then auto-remove it)
                await self._force_kill_container(container_name)

        except FileNotFoundError:
            logger.error("Docker binary not found — is Docker installed and in PATH?")
            return ExecutionResult(
                stdout="", stderr="Docker not available",
                exit_code=1, time_ms=0, memory_kb=0,
                timed_out=False, oom_killed=False, stage=stage,
            )
        except Exception as e:
            logger.error(f"[SANDBOX:{exec_id}] Subprocess error: {e}", exc_info=True)
            return ExecutionResult(
                stdout="", stderr=f"Execution engine error: {type(e).__name__}",
                exit_code=1, time_ms=0, memory_kb=0,
                timed_out=False, oom_killed=False, stage=stage,
            )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        # ── Decode output ─────────────────────────────────
        stdout = stdout_bytes.decode("utf-8", errors="replace")[:100_000]
        stderr = stderr_bytes.decode("utf-8", errors="replace")[:10_000]

        # ── Detect OOM kill ───────────────────────────────
        # Exit code 137 = SIGKILL, typically from OOM killer
        # But only if we didn't already flag it as a timeout
        if exit_code == DOCKER_OOM_EXIT_CODE and not timed_out:
            oom_killed = True
            logger.info(
                f"[SANDBOX:{exec_id}] OOM kill detected (exit_code=137, stage={stage})"
            )

        # ── Debug logging for non-zero exit codes ─────────
        if exit_code != 0 and not timed_out and not oom_killed:
            logger.warning(
                f"[SANDBOX:{exec_id}] Non-zero exit (stage={stage}): "
                f"exit_code={exit_code}, "
                f"stderr={repr(stderr[:1000])}"
            )

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            time_ms=elapsed_ms,
            memory_kb=0,  # Cannot get from --rm containers; use 0
            timed_out=timed_out,
            oom_killed=oom_killed,
            stage=stage,
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Container cleanup helpers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @staticmethod
    async def _force_kill_container(name: str):
        """Send SIGKILL to a running container. --rm will auto-remove it after."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "kill", name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=5)
        except Exception:
            pass


# ── Singleton ─────────────────────────────────────────────────
sandbox = Sandbox()
