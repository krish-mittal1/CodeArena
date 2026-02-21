"""
Judge service — compare actual output against expected output.
No fake logic, real line-by-line comparison.
"""

import logging

from backend.core.constants import Verdict

logger = logging.getLogger(__name__)


def judge(
    actual_output: str,
    expected_output: str,
    exit_code: int,
    timed_out: bool,
    oom_killed: bool,
) -> Verdict:
    """
    Determine the verdict for a single test case execution.

    Args:
        actual_output: stdout from the sandbox (may be None or empty)
        expected_output: expected output from the test case (may be None)
        exit_code: process exit code (0 = success)
        timed_out: whether the process exceeded time limit
        oom_killed: whether the process was killed for exceeding memory

    Returns:
        Verdict enum value
    """
    # ── Priority 1: TLE (most specific) ───────────────────
    if timed_out:
        logger.info(f"[JUDGE] Verdict=TLE (timed_out=True)")
        return Verdict.TLE

    # ── Priority 2: MLE ───────────────────────────────────
    if oom_killed:
        logger.info(f"[JUDGE] Verdict=MLE (oom_killed=True)")
        return Verdict.MLE

    # ── Priority 3: Runtime error (non-zero exit) ─────────
    if exit_code != 0:
        logger.info(
            f"[JUDGE] Verdict=RUNTIME_ERROR (exit_code={exit_code})"
        )
        return Verdict.RUNTIME_ERROR

    # ── Priority 4: Compare output ────────────────────────
    # Handle None inputs safely — treat as empty string
    actual = actual_output if actual_output is not None else ""
    expected = expected_output if expected_output is not None else ""

    actual_lines = _normalize_output(actual)
    expected_lines = _normalize_output(expected)

    if actual_lines == expected_lines:
        logger.debug(f"[JUDGE] Verdict=ACCEPTED")
        return Verdict.ACCEPTED

    # Log mismatch details for debugging
    logger.info(
        f"[JUDGE] Verdict=WRONG_ANSWER "
        f"(actual_lines={len(actual_lines)}, expected_lines={len(expected_lines)}, "
        f"actual_preview={repr(actual[:200])}, expected_preview={repr(expected[:200])})"
    )
    return Verdict.WRONG_ANSWER


def _normalize_output(output: str) -> list[str]:
    """
    Normalize output for comparison:
    - Strip leading/trailing whitespace from the entire output
    - Split into lines
    - Strip trailing whitespace from each line (but preserve internal spaces)
    - Remove trailing empty lines
    """
    if not output:
        return []

    lines = [line.rstrip() for line in output.strip().split("\n")]

    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()

    return lines
