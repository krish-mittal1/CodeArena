from __future__ import annotations

"""
Docker sandbox — secure, isolated code execution via subprocess.
"""

import os
import time
import uuid
import asyncio
import tempfile
import logging
import subprocess
from dataclasses import dataclass

from backend.config import settings
from backend.execution.languages import get_language_config

logger = logging.getLogger(__name__)

DOCKER_OOM_EXIT_CODE = 137
TIMEOUT_EXIT_CODE = 124

MAX_CONCURRENT_CONTAINERS = 4
_container_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONTAINERS)


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
        time_limit_ms: int | None = None,
        memory_limit_mb: int | None = None,
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

        async with _container_semaphore:

            # Use /tmp/codearena which is shared between API container and host
            # (required for Docker-in-Docker volume mounts to work)
            os.makedirs("/tmp/codearena", exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=f"codearena_{exec_id}_", dir="/tmp/codearena") as tmpdir:

                # ── Write source code
                filename = (
                    f"Solution{config.file_extension}"
                    if language == "java"
                    else f"code{config.file_extension}"
                )

                code_path = os.path.join(tmpdir, filename)
                with open(code_path, "w", encoding="utf-8") as f:
                    f.write(code)

                # ── Write input
                stdin_path = os.path.join(tmpdir, "input.txt")
                with open(stdin_path, "w", encoding="utf-8") as f:
                    f.write(stdin_data or "")

                # ── Compilation step (if needed)
                if config.needs_compilation:
                    compile_result = await self._run_compile(
                        exec_id, config, tmpdir, mem_mb
                    )
                    if compile_result is not None:
                        return compile_result

                # ── Build run command
                inner_cmd = f"{config.run_cmd} < /sandbox/input.txt"

                # ── Docker command
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
                    "-v", f"{tmpdir}:/sandbox:rw",

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


    async def _run_compile(
        self,
        exec_id: str,
        config,
        tmpdir: str,
        mem_mb: int,
    ) -> ExecutionResult | None:

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
            "-v", f"{tmpdir}:/sandbox:rw",

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