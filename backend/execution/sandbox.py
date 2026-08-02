from __future__ import annotations

"""
Docker sandbox — secure, isolated code execution via subprocess.
"""

import os
import math
import time
import uuid
import asyncio
import tempfile
import logging
import subprocess
from dataclasses import dataclass
from typing import Optional

from backend.config import settings
from backend.execution.languages import get_language_config
from backend.execution.drivers import generate_driver

logger = logging.getLogger(__name__)

DOCKER_OOM_EXIT_CODE = 137
TIMEOUT_EXIT_CODE = 124

# Shared across judge workers and practice Run — configurable via settings.
_container_semaphore = asyncio.Semaphore(settings.sandbox_max_concurrent)


async def _acquire_container_slot() -> None:
    """
    Wait for a free sandbox slot, failing fast if the pool is saturated.

    Practice Run and judge share this semaphore so API requests cannot spawn
    unbounded Docker containers under load.
    """
    try:
        await asyncio.wait_for(
            _container_semaphore.acquire(),
            timeout=settings.sandbox_acquire_timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        raise TimeoutError(
            f"Sandbox capacity exhausted "
            f"(max_concurrent={settings.sandbox_max_concurrent}, "
            f"waited={settings.sandbox_acquire_timeout_seconds}s)"
        ) from exc


# Docker-in-Docker path translation:
# The API container writes files to /app/.sandbox_tmp/ (container path).
# Compose mounts ./.sandbox_tmp → /app/.sandbox_tmp; SANDBOX_HOST_WORKDIR is
# the host project dir so runner -v flags use $SANDBOX_HOST_WORKDIR/.sandbox_tmp/.
_CONTAINER_APP_DIR = "/app"
_HOST_WORKDIR = os.environ.get("SANDBOX_HOST_WORKDIR", _CONTAINER_APP_DIR)

def _to_host_path(container_path: str) -> str:
    """Translate a container path under /app/ to the equivalent host path."""
    rel = os.path.relpath(container_path, _CONTAINER_APP_DIR)
    return os.path.join(_HOST_WORKDIR, rel)


def _ensure_sandbox_tmp() -> str:
    """Create the dedicated sandbox scratch dir (not world-writable)."""
    sandbox_tmp = os.path.join(_CONTAINER_APP_DIR, ".sandbox_tmp")
    os.makedirs(sandbox_tmp, exist_ok=True)
    try:
        os.chmod(sandbox_tmp, 0o700)
    except OSError:
        pass
    return sandbox_tmp


def _chmod_tree(path: str, mode: int) -> None:
    """Best-effort chmod for files under path (defense in depth before RO mount)."""
    try:
        os.chmod(path, mode)
    except OSError:
        pass
    if not os.path.isdir(path):
        return
    for root, dirs, files in os.walk(path):
        for name in dirs:
            try:
                os.chmod(os.path.join(root, name), mode)
            except OSError:
                pass
        for name in files:
            try:
                os.chmod(os.path.join(root, name), mode)
            except OSError:
                pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Structured result
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    time_ms: int
    memory_kb: int
    timed_out: bool
    oom_killed: bool
    stage: str

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

    async def execute(
        self,
        language: str,
        code: str,
        stdin_data: str,
        time_limit_ms: Optional[int] = None,
        memory_limit_mb: Optional[int] = None,
    ) -> ExecutionResult:

        exec_id = uuid.uuid4().hex[:8]
        config = get_language_config(language)

        timeout_seconds = (time_limit_ms / 1000.0) if time_limit_ms else 2.0

        mem_limit_str = settings.sandbox_memory_limit.rstrip("mM")
        try:
            mem_mb = memory_limit_mb or int(mem_limit_str)
        except ValueError:
            mem_mb = memory_limit_mb or 256

        if stdin_data and not stdin_data.endswith("\n"):
            stdin_data += "\n"

        # Write temp files under /app/.sandbox_tmp/ (dedicated compose mount)
        sandbox_tmp = _ensure_sandbox_tmp()

        with tempfile.TemporaryDirectory(prefix=f"codearena_{exec_id}_", dir=sandbox_tmp) as tmpdir:
            os.chmod(tmpdir, 0o755)

            # ── Write source code
            filename = (
                f"Solution{config.file_extension}"
                if language == "java"
                else f"code{config.file_extension}"
            )

            code_path = os.path.join(tmpdir, filename)
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            os.chmod(code_path, 0o644)

            # ── Write input
            stdin_path = os.path.join(tmpdir, "input.txt")
            with open(stdin_path, "w", encoding="utf-8") as f:
                f.write(stdin_data or "")
            os.chmod(stdin_path, 0o644)

            await _acquire_container_slot()
            try:

                # ── Compilation step (if needed) — needs RW
                if config.needs_compilation:
                    compile_result = await self._run_compile(
                        exec_id, config, tmpdir, mem_mb
                    )
                    if compile_result is not None:
                        return compile_result

                # Lock down inputs/code before the submission process runs
                _chmod_tree(tmpdir, 0o555)

                # ── Build run command
                inner_cmd = f"{config.run_cmd} < /sandbox/input.txt"

                # ── Docker command — RO workspace (stdout captured from process)
                container_name = f"codearena-{exec_id}"

                docker_args = [
                    "docker", "run",
                    "--name", container_name,

                    "--network", "none",
                    "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges:true",

                    "--memory", f"{mem_mb}m",
                    "--memory-swap", f"{mem_mb}m",
                    "--pids-limit", str(settings.sandbox_pids_limit),
                    "--ulimit", "stack=67108864:67108864", # 64MB stack size
                    "--cpus", "0.5",

                    "--tmpfs", "/tmp:size=64m,nosuid",
                    "-v", f"{_to_host_path(tmpdir)}:/sandbox:ro",

                    "--rm",
                    "--entrypoint", "sh",

                    config.image,
                    "-c", inner_cmd,
                ]

                result = await self._run_process(
                    exec_id,
                    docker_args,
                    container_name,
                    timeout_seconds,
                    stage="run",
                )

                return result
            finally:
                _container_semaphore.release()


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Batch execution — compile once, run ALL tests in ONE container
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def execute_batch(
        self,
        language: str,
        code: str,
        test_inputs: list[str],
        time_limit_ms: Optional[int] = None,
        memory_limit_mb: Optional[int] = None,
        problem_meta: Optional[dict] = None,
    ) -> list[ExecutionResult]:
        """
        Execute code against multiple test inputs in a SINGLE Docker container.

        1. Write source code + all test input files to a shared temp dir
        2. Compile once (if needed) in one container
        3. Create a runner script that loops through all inputs
        4. Run the runner in ONE container — each test is a child process
        5. Read per-test output/error/meta files and return results

        This reduces N test cases from N (or 2N) Docker containers down to
        1 compile container + 1 run container = 2 containers total.
        """
        if not test_inputs:
            return []

        exec_id = uuid.uuid4().hex[:8]
        config = get_language_config(language)
        num_tests = len(test_inputs)

        timeout_per_test = (time_limit_ms / 1000.0) if time_limit_ms else 2.0

        mem_limit_str = settings.sandbox_memory_limit.rstrip("mM")
        try:
            mem_mb = memory_limit_mb or int(mem_limit_str)
        except ValueError:
            mem_mb = memory_limit_mb or 256

        sandbox_tmp = _ensure_sandbox_tmp()

        with tempfile.TemporaryDirectory(prefix=f"codearena_{exec_id}_", dir=sandbox_tmp) as tmpdir:
            # in/: code, driver, inputs, runner, binaries (RO during run)
            # out/: per-test stdout/stderr/meta (RW only)
            in_dir = os.path.join(tmpdir, "in")
            out_dir = os.path.join(tmpdir, "out")
            os.makedirs(in_dir, mode=0o755)
            os.makedirs(out_dir, mode=0o755)
            os.chmod(tmpdir, 0o755)

            # ── Write source code (once) ──────────────────
            # In LeetCode driver mode for Python, save as solution.py
            # to avoid collision with Python's built-in 'code' module
            is_driver_mode = problem_meta and problem_meta.get("method_name")
            if language == "java":
                filename = f"Solution{config.file_extension}"
            elif language == "python" and is_driver_mode:
                filename = f"solution{config.file_extension}"
            else:
                filename = f"code{config.file_extension}"
            code_path = os.path.join(in_dir, filename)
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            os.chmod(code_path, 0o644)

            # ── Generate and write driver (LeetCode mode) ──
            driver_code = None
            driver_filename = None
            if problem_meta and problem_meta.get("method_name"):
                driver_code = generate_driver(
                    language=language,
                    method_name=problem_meta["method_name"],
                    parameters=problem_meta.get("parameters", []),
                    return_type=problem_meta.get("return_type", "int"),
                )
            
            if driver_code:
                if language == "python":
                    driver_filename = "driver.py"
                elif language == "javascript":
                    driver_filename = "driver.js"
                elif language == "cpp":
                    driver_filename = "driver.cpp"
                elif language == "java":
                    driver_filename = "Main.java"
                
                if driver_filename:
                    driver_path = os.path.join(in_dir, driver_filename)
                    with open(driver_path, "w", encoding="utf-8") as f:
                        f.write(driver_code)
                    os.chmod(driver_path, 0o644)
                    logger.info(f"[SANDBOX] {exec_id}: LeetCode driver injected ({driver_filename})")

            # ── Write ALL test inputs ─────────────────────
            for i, inp in enumerate(test_inputs):
                inp_data = inp or ""
                if inp_data and not inp_data.endswith("\n"):
                    inp_data += "\n"
                inp_path = os.path.join(in_dir, f"input_{i}.txt")
                with open(inp_path, "w", encoding="utf-8") as f:
                    f.write(inp_data)
                os.chmod(inp_path, 0o644)

            await _acquire_container_slot()
            try:

                # ── Compile once (if needed) ──────────────
                # Skip normal compilation in driver mode for compiled languages
                # (C++/Java) — the driver handles its own compilation below
                if config.needs_compilation and not (driver_code and language in ("cpp", "java")):
                    compile_result = await self._run_compile(
                        exec_id, config, in_dir, mem_mb
                    )
                    if compile_result is not None:
                        # Compilation failed → return same error for ALL tests
                        return [compile_result] * num_tests

                # ── Write runner script ───────────────────
                # Soft wall for `timeout` command: ceil(limit) so we can still
                # observe wall-clock; hard TLE is enforced below via time_ms.
                timeout_s = max(1, math.ceil(timeout_per_test))
                
                # Determine run command: use driver if available (paths under /sandbox/in)
                if driver_code and driver_filename:
                    if language == "python":
                        run_cmd = "python3 /sandbox/in/driver.py"
                    elif language == "javascript":
                        run_cmd = "node /sandbox/in/driver.js"
                    elif language == "cpp":
                        # For C++, driver includes user code via #include
                        run_cmd = "/sandbox/in/solution"  # compiled binary
                    elif language == "java":
                        run_cmd = "java -cp /sandbox/in Main"
                    else:
                        run_cmd = config.run_cmd
                else:
                    # Non-driver: language run_cmd assumes cwd /sandbox with code file
                    # Rewrite common patterns to /sandbox/in
                    run_cmd = (
                        config.run_cmd
                        .replace("/sandbox/", "/sandbox/in/")
                    )
                    if run_cmd == config.run_cmd and " /" not in config.run_cmd:
                        # Relative run cmds (e.g. python3 code.py) need cwd
                        run_cmd = f"cd /sandbox/in && {config.run_cmd}"
                    
                # For C++ with driver, we need to compile the driver file
                if driver_code and language == "cpp":
                    compile_result = await self._run_compile_custom(
                        exec_id, config, in_dir, mem_mb,
                        compile_cmd=f"g++ -O2 -std=gnu++17 -Wall -o /sandbox/solution /sandbox/driver.cpp"
                    )
                    if compile_result is not None:
                        return [compile_result] * num_tests
                elif driver_code and language == "java":
                    # Compile both Main.java (driver) and Solution.java (user code)
                    compile_result = await self._run_compile_custom(
                        exec_id, config, in_dir, mem_mb,
                        compile_cmd="javac /sandbox/Main.java /sandbox/Solution.java -d /sandbox"
                    )
                    if compile_result is not None:
                        return [compile_result] * num_tests

                runner_script = f"""#!/bin/sh
i=0
while [ $i -lt {num_tests} ]; do
    START_NS=$(date +%s%N 2>/dev/null || echo 0)
    timeout {timeout_s}s {run_cmd} < /sandbox/in/input_${{i}}.txt > /sandbox/out/output_${{i}}.txt 2>/sandbox/out/error_${{i}}.txt &
    PID=$!
    PEAK_KB=0
    # Find the actual child process (not the timeout wrapper)
    sleep 0.02
    CHILD_PID=$(cat /proc/$PID/task/$PID/children 2>/dev/null | awk '{{print $1}}')
    if [ -z "$CHILD_PID" ]; then CHILD_PID=$PID; fi
    while kill -0 $PID 2>/dev/null; do
        MEM_FILE="/proc/$CHILD_PID/status"
        if [ -f "$MEM_FILE" ]; then
            CUR_KB=$(grep VmRSS "$MEM_FILE" 2>/dev/null | awk '{{print $2}}')
            if [ -n "$CUR_KB" ] && [ "$CUR_KB" -gt "$PEAK_KB" ] 2>/dev/null; then
                PEAK_KB=$CUR_KB
            fi
        fi
        sleep 0.05
    done
    wait $PID
    EXIT_CODE=$?
    END_NS=$(date +%s%N 2>/dev/null || echo 0)
    if [ "$START_NS" != "0" ] && [ "$END_NS" != "0" ]; then
        ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))
    else
        ELAPSED_MS=0
    fi
    echo "${{EXIT_CODE}}|${{ELAPSED_MS}}|${{PEAK_KB}}" > /sandbox/out/meta_${{i}}.txt
    i=$((i + 1))
done
"""
                runner_path = os.path.join(in_dir, "runner.sh")
                with open(runner_path, "w", encoding="utf-8") as f:
                    f.write(runner_script)
                os.chmod(runner_path, 0o555)

                # Freeze inputs/code/binaries so a test cannot rewrite later inputs
                _chmod_tree(in_dir, 0o555)

                # ── Run ALL tests in ONE container ────────
                # RO mount for inputs/code; separate RW out-only mount
                total_timeout = (timeout_per_test + 1) * num_tests + 15.0
                container_name = f"codearena-batch-{exec_id}"

                docker_args = [
                    "docker", "run",
                    "--name", container_name,

                    "--network", "none",
                    "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges:true",

                    "--memory", f"{mem_mb}m",
                    "--memory-swap", f"{mem_mb}m",
                    "--pids-limit", str(settings.sandbox_pids_limit),
                    "--ulimit", "stack=67108864:67108864",
                    "--cpus", "0.5",

                    "--tmpfs", "/tmp:size=64m,nosuid",
                    "-v", f"{_to_host_path(in_dir)}:/sandbox/in:ro",
                    "-v", f"{_to_host_path(out_dir)}:/sandbox/out:rw",

                    "--rm",
                    "--entrypoint", "sh",

                    config.image,
                    "/sandbox/in/runner.sh",
                ]

                batch_timed_out = False
                try:
                    def _sync_run():
                        return subprocess.run(
                            docker_args,
                            capture_output=True,
                            timeout=total_timeout + 5.0,
                        )

                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, _sync_run)

                except subprocess.TimeoutExpired:
                    batch_timed_out = True
                    await self._force_kill_container(container_name)

                except Exception as e:
                    err = ExecutionResult(
                        stdout="",
                        stderr=f"Batch execution error: {type(e).__name__}: {e}",
                        exit_code=1, time_ms=0, memory_kb=0,
                        timed_out=False, oom_killed=False, stage="run",
                    )
                    return [err] * num_tests

                # ── Parse per-test results ────────────────
                results: list[ExecutionResult] = []
                for i in range(num_tests):
                    stdout = self._read_file_safe(
                        os.path.join(out_dir, f"output_{i}.txt")
                    )
                    stderr = self._read_file_safe(
                        os.path.join(out_dir, f"error_{i}.txt")
                    )
                    meta = self._read_file_safe(
                        os.path.join(out_dir, f"meta_{i}.txt")
                    )

                    exit_code = 1
                    time_ms = 0
                    memory_kb = 0
                    tc_timed_out = False
                    oom_killed = False

                    if meta:
                        parts = meta.strip().split("|")
                        if len(parts) >= 2:
                            try:
                                exit_code = int(parts[0])
                                time_ms = int(parts[1])
                            except ValueError:
                                pass
                        if len(parts) >= 3:
                            try:
                                memory_kb = int(parts[2])
                            except ValueError:
                                pass
                    else:
                        # No meta file means test never ran or container crashed
                        if batch_timed_out:
                            tc_timed_out = True
                            exit_code = TIMEOUT_EXIT_CODE
                        elif i > 0 and not stdout and not stderr:
                            oom_killed = True
                            exit_code = DOCKER_OOM_EXIT_CODE

                    # timeout command returns 124 on timeout
                    if exit_code == TIMEOUT_EXIT_CODE:
                        tc_timed_out = True

                    # Hard TLE: measured time exceeds problem limit even if soft
                    # wall allowed the process to finish.
                    time_limit_ms_int = int(timeout_per_test * 1000)
                    if time_ms > 0 and time_ms > time_limit_ms_int:
                        tc_timed_out = True

                    # Docker OOM killer returns 137
                    if exit_code == DOCKER_OOM_EXIT_CODE:
                        oom_killed = True

                    results.append(ExecutionResult(
                        stdout=stdout[:2_000_000],
                        stderr=stderr[:10_000],
                        exit_code=exit_code,
                        time_ms=time_ms,
                        memory_kb=memory_kb,
                        timed_out=tc_timed_out,
                        oom_killed=oom_killed,
                        stage="run",
                    ))
                # If batch container itself timed out, fill remaining with TLE
                if batch_timed_out and len(results) < num_tests:
                    for _ in range(num_tests - len(results)):
                        results.append(ExecutionResult(
                            stdout="", stderr="Container batch timed out",
                            exit_code=TIMEOUT_EXIT_CODE, time_ms=0,
                            memory_kb=0, timed_out=True,
                            oom_killed=False, stage="run",
                        ))

                return results
            finally:
                _container_semaphore.release()

    @staticmethod
    def _read_file_safe(path: str) -> str:
        """Read a file, returning empty string if it doesn't exist."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except (FileNotFoundError, OSError):
            return ""


    async def _run_compile(
        self,
        exec_id: str,
        config,
        tmpdir: str,
        mem_mb: int,
    ) -> Optional[ExecutionResult]:

        container_name = f"codearena-compile-{exec_id}"
        compile_cmd = f"cd /sandbox && {config.compile_cmd}"

        docker_args = [
            "docker", "run",
            "--name", container_name,

            "--network", "none",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",

            "--memory", "512m", # Assign a fixed massive compilation memory separate from user execution limits
            "--memory-swap", "512m",
            "--pids-limit", str(settings.sandbox_pids_limit),
            "--ulimit", "stack=67108864:67108864",
            "--cpus", "0.5",

            "--tmpfs", "/tmp:size=64m,nosuid",
            "-v", f"{_to_host_path(tmpdir)}:/sandbox:rw",

            "--rm",
            "--entrypoint", "sh",

            config.image,
            "-c", compile_cmd,
        ]

        result = await self._run_process(
            exec_id,
            docker_args,
            container_name,
            settings.sandbox_compile_timeout,
            stage="compile",
        )

        if result.exit_code != 0:
            return result

        return None


    async def _run_compile_custom(
        self,
        exec_id: str,
        config,
        tmpdir: str,
        mem_mb: int,
        compile_cmd: str = "",
    ) -> Optional[ExecutionResult]:
        """Compile with a custom command (used for driver-based compilation)."""
        container_name = f"codearena-compile-drv-{exec_id}"
        full_cmd = f"cd /sandbox && {compile_cmd}"

        docker_args = [
            "docker", "run",
            "--name", container_name,
            "--network", "none",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--memory", "512m",
            "--memory-swap", "512m",
            "--pids-limit", str(settings.sandbox_pids_limit),
            "--ulimit", "stack=67108864:67108864",
            "--cpus", "0.5",
            "--tmpfs", "/tmp:size=64m,nosuid",
            "-v", f"{_to_host_path(tmpdir)}:/sandbox:rw",
            "--rm",
            "--entrypoint", "sh",
            config.image,
            "-c", full_cmd,
        ]

        result = await self._run_process(
            exec_id,
            docker_args,
            container_name,
            settings.sandbox_compile_timeout,
            stage="compile",
        )

        if result.exit_code != 0:
            return result

        return None


    async def _run_process(
        self,
        exec_id: str,
        docker_args: list[str],
        container_name: str,
        timeout_seconds: float,
        stage: str,
    ) -> ExecutionResult:

        timed_out = False
        oom_killed = False
        stdout_bytes = b""
        stderr_bytes = b""
        exit_code = 1
        start_time = time.monotonic()

        def _sync_run():
            return subprocess.run(
                docker_args,
                capture_output=True,
                timeout=timeout_seconds + 5.0,
            )

        try:
            loop = asyncio.get_event_loop()
            proc = await loop.run_in_executor(None, _sync_run)
            stdout_bytes = proc.stdout
            stderr_bytes = proc.stderr
            exit_code = proc.returncode
            
        except subprocess.TimeoutExpired as e:
            timed_out = True
            exit_code = -1
            if e.stdout:
                stdout_bytes = e.stdout
            if e.stderr:
                stderr_bytes = e.stderr
            await self._force_kill_container(container_name)

        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=f"Execution engine error: {type(e).__name__}: {str(e)}",
                exit_code=1,
                time_ms=0,
                memory_kb=0,
                timed_out=False,
                oom_killed=False,
                stage=stage,
            )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        stdout = stdout_bytes.decode("utf-8", errors="replace")[:100_000]
        stderr = stderr_bytes.decode("utf-8", errors="replace")[:10_000]

        if timed_out and not stderr:
            stderr = "Execution Timeout - The sandbox container did not respond in time or Docker daemon frozen."

        if exit_code == DOCKER_OOM_EXIT_CODE and not timed_out:
            oom_killed = True

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            time_ms=elapsed_ms,
            memory_kb=0,
            timed_out=timed_out,
            oom_killed=oom_killed,
            stage=stage,
        )


    @staticmethod
    async def _force_kill_container(name: str):
        def _kill():
            subprocess.run(
                ["docker", "kill", name],
                capture_output=True,
                timeout=5.0
            )
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _kill)
        except Exception:
            pass

sandbox = Sandbox()