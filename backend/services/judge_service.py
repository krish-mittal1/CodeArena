"""
Judge service — compare actual output against expected output.
Supports both:
  1. Traditional line-by-line string comparison (competitive programming)
  2. JSON-based structural comparison (LeetCode driver mode)
  3. Custom checkers for specific problems (e.g., 3 Sum)
"""

import json
import logging
import re
from typing import Any

from backend.core.constants import Verdict

logger = logging.getLogger(__name__)


def judge(
    actual_output: str,
    expected_output: str,
    exit_code: int,
    timed_out: bool,
    oom_killed: bool,
    problem_title: str = None,
    is_leetcode_mode: bool = False,
) -> Verdict:
    """
    Determine the verdict for a single test case execution.

    Args:
        actual_output: stdout from the sandbox (may be None or empty)
        expected_output: expected output from the test case (may be None)
        exit_code: process exit code (0 = success)
        timed_out: whether the process exceeded time limit
        oom_killed: whether the process was killed for exceeding memory
        problem_title: title of the problem (for custom checkers)
        is_leetcode_mode: if True, use JSON structural comparison

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
    actual = actual_output if actual_output is not None else ""
    expected = expected_output if expected_output is not None else ""

    # LeetCode driver mode: JSON structural comparison
    if is_leetcode_mode:
        return _judge_json(actual, expected)

    # Legacy custom checker for 3 Sum (non-driver mode fallback)
    if problem_title in ("3 Sum", "3Sum", "Three Sum", "ThreeSum") and not is_leetcode_mode:
        return _judge_3_sum(actual, expected)

    # Standard line-by-line comparison
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
    - Split into lines
    - Strip trailing whitespace from each line (but preserve internal spaces)
    - Remove trailing empty lines
    - Remove leading empty lines
    Note: leading/trailing blank lines are stripped symmetrically to avoid
    false positives from programs that print extra newlines.
    """
    if not output:
        return []

    lines = [line.rstrip() for line in output.split("\n")]

    while lines and lines[-1] == "":
        lines.pop()

    while lines and lines[0] == "":
        lines.pop(0)

    return lines


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  JSON-based comparison (LeetCode driver mode)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _normalize_json_value(val: Any, sort_lists: bool = False) -> Any:
    """
    Recursively normalize a parsed JSON value for comparison.
    Only sorts when sort_lists=True (for nested lists like 3Sum).
    """
    if isinstance(val, list):
        normalized = [_normalize_json_value(item, sort_lists=True) for item in val]
        if sort_lists:
            try:
                normalized.sort()
            except TypeError:
                pass
        return normalized
    return val


def _judge_json(actual: str, expected: str) -> Verdict:
    """
    Parse both outputs as JSON, normalize, and compare structurally.
    This handles order-independent comparison of arrays/lists.
    """
    try:
        actual_val = json.loads(actual.strip())
    except (json.JSONDecodeError, ValueError):
        logger.info(
            f"[JUDGE] Verdict=WRONG_ANSWER (JSON parse failed for actual output) "
            f"actual_preview={repr(actual[:300])}"
        )
        return Verdict.WRONG_ANSWER

    try:
        expected_val = json.loads(expected.strip())
    except (json.JSONDecodeError, ValueError):
        # If expected isn't valid JSON, fall back to string comparison
        logger.warning(f"[JUDGE] Expected output is not valid JSON, falling back to string comparison")
        actual_lines = _normalize_output(actual)
        expected_lines = _normalize_output(expected)
        if actual_lines == expected_lines:
            return Verdict.ACCEPTED
        return Verdict.WRONG_ANSWER

    # Normalize both values
    actual_normalized = _normalize_json_value(actual_val)
    expected_normalized = _normalize_json_value(expected_val)

    if actual_normalized == expected_normalized:
        logger.debug("[JUDGE] Verdict=ACCEPTED (JSON comparison)")
        return Verdict.ACCEPTED

    logger.info(
        f"[JUDGE] Verdict=WRONG_ANSWER (JSON comparison)\n"
        f"        ACTUAL={repr(str(actual_normalized)[:300])}\n"
        f"      EXPECTED={repr(str(expected_normalized)[:300])}"
    )
    return Verdict.WRONG_ANSWER


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Custom 3 Sum checker (legacy stdin/stdout fallback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_3sum_output(text: str, is_expected: bool = False) -> list[tuple[int, int, int]]:
    tokens = re.findall(r'-?\d+', text)
    nums = [int(x) for x in tokens]
    if not nums:
        return []
    
    if is_expected:
        nums = nums[1:]
    else:
        if (len(nums) - 1) % 3 == 0 and nums[0] == (len(nums) - 1) // 3:
            nums = nums[1:]
        elif len(nums) % 3 == 1:
            nums = nums[1:]

    triplets = []
    valid_length = (len(nums) // 3) * 3
    for i in range(0, valid_length, 3):
        t = (nums[i], nums[i+1], nums[i+2])
        triplets.append(tuple(sorted(t)))

    unique_triplets = list(set(triplets))
    unique_triplets.sort()
    return unique_triplets


def _judge_3_sum(actual: str, expected: str) -> Verdict:
    actual_triplets = _parse_3sum_output(actual, is_expected=False)
    expected_triplets = _parse_3sum_output(expected, is_expected=True)

    if actual_triplets == expected_triplets:
        logger.debug("[JUDGE] Verdict=ACCEPTED (Custom 3 Sum)")
        return Verdict.ACCEPTED
    
    logger.info(
        f"[JUDGE] Verdict=WRONG_ANSWER (Custom 3 Sum)\n"
        f"        ACTUAL={actual_triplets}\n"
        f"      EXPECTED={expected_triplets}"
    )
    return Verdict.WRONG_ANSWER
