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
from typing import Any, Optional

from backend.core.constants import Verdict

logger = logging.getLogger(__name__)

# Unordered JSON output modes (Meta "return in any order"):
#
#   "deep"  — sort lists at every nesting level. Use when both the outer
#             collection and nested groups are order-insensitive
#             (e.g. 3Sum triplets, Group Anagrams groups+strings, Subsets).
#
#   "outer" — sort only the outermost list; preserve inner list order.
#             Use for list-of-lists where groups may be reordered but
#             pairs/coords/permutations must stay intact (K Closest,
#             Permutations). Flat "any order" arrays also use outer.
#
# Prefer presentation["unordered_output"] when set; else title allowlist.
_UNORDERED_OUTPUT_MODES: dict[str, str] = {
    # deep — nested order also free
    "3 Sum": "deep",
    "3Sum": "deep",
    "Three Sum": "deep",
    "ThreeSum": "deep",
    "4Sum": "deep",
    "Group Anagrams": "deep",
    "Subsets": "deep",
    "Combination Sum": "deep",
    # outer — top-level any order; keep nested sequences
    "Two Sum": "outer",
    "Permutations": "outer",
    "Letter Combinations of a Phone Number": "outer",
    "Top K Frequent Elements": "outer",
    "Find All Anagrams in a String": "outer",
    "Intersection of Two Arrays": "outer",
    "K Closest Points to Origin": "outer",
}

_VALID_UNORDERED_MODES = frozenset({"deep", "outer"})


def judge(
    actual_output: str,
    expected_output: str,
    exit_code: int,
    timed_out: bool,
    oom_killed: bool,
    problem_title: str = None,
    is_leetcode_mode: bool = False,
    unordered_mode: Optional[str] = None,
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
        unordered_mode: optional "deep"|"outer" override (from problem meta)

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
        return _judge_json(
            actual,
            expected,
            problem_title=problem_title,
            unordered_mode=unordered_mode,
        )

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

def _json_sort_key(item: Any) -> Any:
    """Stable sort key for heterogeneous / nested JSON list elements."""
    if isinstance(item, list):
        return (0, [_json_sort_key(x) for x in item])
    if isinstance(item, dict):
        return (1, sorted((k, _json_sort_key(v)) for k, v in item.items()))
    if isinstance(item, bool):
        return (2, item)
    if isinstance(item, (int, float)):
        return (3, item)
    if isinstance(item, str):
        return (4, item)
    if item is None:
        return (5, 0)
    return (6, str(item))


def _normalize_json_value(
    val: Any,
    mode: Optional[str] = None,
    *,
    depth: int = 0,
) -> Any:
    """
    Recursively normalize a parsed JSON value for comparison.

    mode=None  — preserve list order at every level (default)
    mode=deep  — sort every list level
    mode=outer — sort only the outermost list; keep nested order
    """
    if isinstance(val, list):
        normalized = [
            _normalize_json_value(item, mode=mode, depth=depth + 1) for item in val
        ]
        sort_here = mode == "deep" or (mode == "outer" and depth == 0)
        if sort_here:
            try:
                normalized.sort(key=_json_sort_key)
            except TypeError:
                pass
        return normalized
    if isinstance(val, dict):
        return {
            k: _normalize_json_value(v, mode=mode, depth=depth)
            for k, v in val.items()
        }
    return val


def _resolve_unordered_mode(
    problem_title: Optional[str],
    unordered_mode: Optional[str] = None,
) -> Optional[str]:
    """Resolve unordered compare mode from metadata override or title allowlist."""
    if unordered_mode in _VALID_UNORDERED_MODES:
        return unordered_mode
    if not problem_title:
        return None
    return _UNORDERED_OUTPUT_MODES.get(problem_title)


def _judge_json(
    actual: str,
    expected: str,
    problem_title: Optional[str] = None,
    unordered_mode: Optional[str] = None,
) -> Verdict:
    """
    Parse both outputs as JSON, normalize, and compare structurally.

    Order is preserved by default. Known unordered problems sort via
    deep or outer mode (see _UNORDERED_OUTPUT_MODES).
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

    mode = _resolve_unordered_mode(problem_title, unordered_mode)
    actual_normalized = _normalize_json_value(actual_val, mode=mode)
    expected_normalized = _normalize_json_value(expected_val, mode=mode)

    if actual_normalized == expected_normalized:
        logger.debug(
            "[JUDGE] Verdict=ACCEPTED (JSON comparison, unordered_mode=%s)",
            mode,
        )
        return Verdict.ACCEPTED

    logger.info(
        f"[JUDGE] Verdict=WRONG_ANSWER (JSON comparison, unordered_mode={mode})\n"
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
