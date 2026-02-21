"""
Sandbox service — execute user code in isolated Docker containers.

Architecture:
  1. Write user code + test input to a temp directory
  2. Run Docker container with strict resource limits
  3. Read output + result.json from the temp directory
  4. Return structured SandboxResult

Security:
  - No network access (network_mode="none")
  - Non-root user inside container
  - CPU quota, memory limit, PID limit
  - Timeout enforced by both shell (timeout cmd) and Docker (--stop-timeout)
  - Read-only root filesystem (user writes only to /workspace)
"""

import json
import logging
import os
import tempfile
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import docker
from docker.errors import ContainerError, ImageNotFound, APIError

from backend.config import settings

logger = logging.getLogger(__name__)

SANDBOX_IMAGE = "codearena-sandbox"

# Language → (source filename, env value)
LANGUAGE_MAP = {
    "cpp": ("code.cpp", "cpp"),
    "python": ("code.py", "python"),
}


@dataclass
class SandboxResult:
    """Result from a single sandbox execution."""
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    oom_killed: bool
    time_ms: int
    memory_kb: int
    stage: str  # "compile" or "run"


def _get_docker_client() -> docker.DockerClient:
    """Get Docker client. Uses DOCKER_HOST env or default socket."""
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        logger.error(f"Cannot connect to Docker: {e}")
        raise RuntimeError(
            "Docker is not available. Ensure Docker Desktop is running."
        ) from e


def run_code(
    code: str,
    language: str,
    input_data: str,
    time_limit_ms: int = 2000,
    memory_limit_mb: int = 256,
) -> SandboxResult:
    """
    Execute user code in a Docker sandbox.

    This is a BLOCKING call — designed to be run in a thread/worker,
    not in the async event loop.

    Args:
        code: Source code string
        language: "cpp" or "python"
        input_data: stdin input for the program
        time_limit_ms: Execution time limit in milliseconds
        memory_limit_mb: Memory limit in MB

    Returns:
        SandboxResult with stdout, stderr, verdict metadata
    """
    # Generate a unique execution ID for logging
    exec_id = uuid.uuid4().hex[:8]

    if language not in LANGUAGE_MAP:
        logger.warning(f"[SANDBOX:{exec_id}] Unsupported language: {language}")
        return SandboxResult(
            stdout="",
            stderr=f"Unsupported language: {language}",
            exit_code=1,
            timed_out=False,
            oom_killed=False,
            time_ms=0,
            memory_kb=0,
            stage="compile",
        )

    source_filename, lang_env = LANGUAGE_MAP[language]

    # ── Ensure input ends with newline ─────────────────────
    # Programs using line-based input (scanf, getline, input())
    # may hang or read incomplete data without a trailing newline.
    if input_data and not input_data.endswith("\n"):
        input_data += "\n"

    logger.info(
        f"[SANDBOX:{exec_id}] Starting execution: "
        f"lang={language}, input_len={len(input_data)}, "
        f"time_limit={time_limit_ms}ms, mem_limit={memory_limit_mb}MB, "
        f"input_preview={repr(input_data[:200])}"
    )

    # Create temp directory with UNIQUE name to prevent race conditions
    work_dir = tempfile.mkdtemp(prefix=f"codearena_{exec_id}_")

    try:
        # Write source file
        with open(os.path.join(work_dir, source_filename), "w", encoding="utf-8") as f:
            f.write(code)

        # Write input file
        with open(os.path.join(work_dir, "input.txt"), "w", encoding="utf-8") as f:
            f.write(input_data)

        # Calculate time limit in seconds (minimum 2s for overhead)
        time_limit_secs = max(2, (time_limit_ms // 1000) + 1)

        # Total container timeout — compile + run + buffer
        container_timeout = settings.sandbox_total_timeout

        try:
            client = _get_docker_client()
        except RuntimeError as e:
            logger.error(f"[SANDBOX:{exec_id}] Docker unavailable: {e}")
            return SandboxResult(
                stdout="",
                stderr=f"Execution engine unavailable: {e}",
                exit_code=1,
                timed_out=False,
                oom_killed=False,
                time_ms=0,
                memory_kb=0,
                stage="run",
            )

        # Run container
        container = None
        try:
            container = client.containers.run(
                image=SANDBOX_IMAGE,
                volumes={work_dir: {"bind": "/workspace", "mode": "rw"}},
                environment={
                    "LANGUAGE": lang_env,
                    "TIME_LIMIT": str(time_limit_secs),
                },
                network_mode="none",               # No network access
                mem_limit=f"{memory_limit_mb}m",    # Memory limit
                memswap_limit=f"{memory_limit_mb}m",  # Disable swap
                cpu_quota=settings.sandbox_cpu_quota,
                cpu_period=settings.sandbox_cpu_period,
                pids_limit=settings.sandbox_pids_limit,
                user="sandbox",
                working_dir="/workspace",
                detach=True,
                remove=False,  # We remove manually after reading results
            )

            # Wait for container to finish (with timeout)
            result = container.wait(timeout=container_timeout)
            container_exit = result.get("StatusCode", 1)

            # ── Reload container to get fresh state (OOM flag) ──
            # CRITICAL: container.attrs is stale after .wait() —
            # we must reload to see OOMKilled status
            try:
                container.reload()
            except Exception as reload_err:
                logger.warning(
                    f"[SANDBOX:{exec_id}] Container reload failed: {reload_err}"
                )

            # Check for OOM kill from Docker's perspective
            oom_killed = container.attrs.get("State", {}).get("OOMKilled", False)

            logger.info(
                f"[SANDBOX:{exec_id}] Container finished: "
                f"exit_code={container_exit}, oom_killed={oom_killed}"
            )

        except Exception as e:
            logger.error(
                f"[SANDBOX:{exec_id}] Container execution error: {e}",
                exc_info=True,
            )
            return SandboxResult(
                stdout="",
                stderr=f"Sandbox error: {str(e)}",
                exit_code=1,
                timed_out=False,
                oom_killed=False,
                time_ms=0,
                memory_kb=0,
                stage="run",
            )
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

        # ── Read results from workspace ───────────────────
        stdout = _read_file(work_dir, "output.txt")
        stderr = _read_file(work_dir, "error.txt")
        result_json = _read_file(work_dir, "result.json")

        # Parse result.json
        if result_json:
            try:
                meta = json.loads(result_json)
            except json.JSONDecodeError:
                logger.warning(
                    f"[SANDBOX:{exec_id}] Invalid result.json: {repr(result_json[:500])}"
                )
                meta = {}
        else:
            logger.warning(
                f"[SANDBOX:{exec_id}] No result.json found — "
                f"container may have crashed before writing it"
            )
            meta = {}

        # ── Build result ──────────────────────────────────
        # Timed_out and oom_killed come from result.json (shell-level detection)
        # OR from Docker-level detection. Either source is valid.
        timed_out = meta.get("timed_out", False)
        # Docker-level OOM overrides shell-level (more reliable)
        oom_killed = oom_killed or meta.get("oom_killed", False)

        sandbox_result = SandboxResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=meta.get("exit_code", container_exit),
            timed_out=timed_out,
            oom_killed=oom_killed,
            time_ms=meta.get("time_ms", 0),
            memory_kb=0,  # Memory tracking requires cgroup stats (future)
            stage=meta.get("stage", "run"),
        )

        logger.info(
            f"[SANDBOX:{exec_id}] Result: "
            f"stage={sandbox_result.stage}, "
            f"exit_code={sandbox_result.exit_code}, "
            f"timed_out={sandbox_result.timed_out}, "
            f"oom_killed={sandbox_result.oom_killed}, "
            f"time_ms={sandbox_result.time_ms}, "
            f"stdout_len={len(sandbox_result.stdout)}, "
            f"stderr_len={len(sandbox_result.stderr)}, "
            f"stderr_preview={repr(sandbox_result.stderr[:300])}"
        )

        return sandbox_result

    finally:
        # Clean up temp directory
        shutil.rmtree(work_dir, ignore_errors=True)


def _read_file(directory: str, filename: str) -> str:
    """Safely read a file from the workspace directory."""
    path = os.path.join(directory, filename)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def ensure_sandbox_image() -> bool:
    """Check if the sandbox Docker image exists, build if not."""
    try:
        client = _get_docker_client()
        try:
            client.images.get(SANDBOX_IMAGE)
            logger.info(f"Sandbox image '{SANDBOX_IMAGE}' found.")
            return True
        except ImageNotFound:
            logger.info(f"Building sandbox image '{SANDBOX_IMAGE}'...")
            sandbox_dir = Path(__file__).resolve().parent.parent.parent / "sandbox"
            if not sandbox_dir.exists():
                logger.error(f"Sandbox directory not found: {sandbox_dir}")
                return False
            client.images.build(
                path=str(sandbox_dir),
                tag=SANDBOX_IMAGE,
                rm=True,
            )
            logger.info(f"Sandbox image '{SANDBOX_IMAGE}' built successfully.")
            return True
    except Exception as e:
        logger.warning(f"Docker not available: {e}. Sandbox execution disabled.")
        return False
