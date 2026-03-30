"""
Seed script — insert/update 'Longest Substring With At Most K Distinct Characters'
with 250+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_longest_substring_k_distinct
"""

import asyncio
import json
import logging
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Longest Substring With At Most K Distinct Characters"


def longest_substring_k_distinct(s: str, k: int) -> int:
    """Reference sliding-window solver: longest subarray with at most k distinct values."""
    if k <= 0:
        return 0
    if k >= len(set(s)):
        return len(s)

    left = 0
    counts: dict[str, int] = {}
    best = 0

    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1

        while len(counts) > k:
            lc = s[left]
            counts[lc] -= 1
            if counts[lc] == 0:
                del counts[lc]
            left += 1

        best = max(best, right - left + 1)

    return best


def make_case(s: str, k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s) + "\n" + json.dumps(k),
        "expected_output": json.dumps(longest_substring_k_distinct(s, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Samples from prompt.
    samples = [
        ("aababbcaacc", 2),
        ("abcddefg", 3),
    ]
    for s, k in samples:
        cases.append(make_case(s, k, idx, is_sample=True))
        idx += 1

    # Edge cases: k=0, k=1, single char, empty-like.
    edge_cases = [
        ("a", 1),
        ("aa", 1),
        ("ab", 1),
        ("ab", 2),
        ("abc", 1),
        ("abc", 2),
        ("abc", 3),
        ("abcabc", 2),
        ("abcabc", 3),
        ("aaaaaa", 1),
        ("aaaaaa", 2),
        ("aabbcc", 1),
        ("aabbcc", 2),
        ("aabbcc", 3),
        ("abcdefghij", 1),
        ("abcdefghij", 5),
        ("abcdefghij", 10),
        ("aaabbbccc", 2),
        ("xyxyxyxy", 1),
        ("xyxyxyxy", 2),
        ("abacabad", 2),
        ("eceba", 2),
        ("dvdf", 3),
    ]
    for s, k in edge_cases:
        cases.append(make_case(s, k, idx))
        idx += 1

    # Structured patterns with varying k.
    for n in [15, 25, 50, 75, 100]:
        # Pattern 1: Alternating 2 chars.
        alt = "".join("ab" * (n // 2))
        for k_val in [1, 2, 3]:
            cases.append(make_case(alt, k_val, idx))
            idx += 1

        # Pattern 2: Cycling through alphabet.
        cycle = "".join(chr(ord('a') + i % 5) for i in range(n))
        for k_val in [1, 2, 3, 5]:
            cases.append(make_case(cycle, k_val, idx))
            idx += 1

        # Pattern 3: Blocks.
        blocks = "a" * (n // 3) + "b" * (n // 3) + "c" * (n - 2 * (n // 3))
        for k_val in [1, 2, 3]:
            cases.append(make_case(blocks, k_val, idx))
            idx += 1

    # Character variety stress.
    for n in [100, 200, 300]:
        all_unique = "".join(chr(ord('a') + (i % 26)) for i in range(n))
        for k_val in [1, 5, 10, 26]:
            if k_val <= 26:
                cases.append(make_case(all_unique, k_val, idx))
                idx += 1

    # k boundary cases.
    for n in [30, 50, 75]:
        s = "".join(chr(ord('a') + (i % 10)) for i in range(n))
        for k_val in [0, 1, 5, 10, 11]:
            if k_val <= 10:
                cases.append(make_case(s, k_val, idx))
                idx += 1

    # Deterministic randomized cases to reach 250+.
    rng = random.Random(20260331)
    while len(cases) < 250:
        n = rng.randint(1, 500)
        k = rng.randint(1, min(10, 26))

        mode = rng.randint(0, 3)
        if mode == 0:
            # Low variety: fewer distinct chars.
            palette_size = min(3, k)
            s = "".join(chr(ord('a') + rng.randint(0, palette_size - 1)) for _ in range(n))
        elif mode == 1:
            # Medium variety.
            palette_size = min(8, k + 2)
            s = "".join(chr(ord('a') + rng.randint(0, palette_size - 1)) for _ in range(n))
        elif mode == 2:
            # High variety: many distinct chars.
            s = "".join(chr(ord('a') + rng.randint(0, 25)) for _ in range(n))
        else:
            # Sparse repeats.
            chars = [chr(ord('a') + i) for i in range(min(k + 3, 26))]
            s = "".join(rng.choice(chars) for _ in range(n))

        cases.append(make_case(s, k, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given a string s and an integer k, find the length of the longest substring "
            "that contains at most k distinct characters.\n\n"
            "A substring is a contiguous sequence of characters within a string.\n\n"
            "Example 1\n"
            "Input: s = \"aababbcaacc\", k = 2\n"
            "Output: 6\n"
            "Explanation: The longest substring with at most 2 distinct characters is \"aababb\" with length 6.\n\n"
            "Example 2\n"
            "Input: s = \"abcddefg\", k = 3\n"
            "Output: 4\n"
            "Explanation: The longest substring with at most 3 distinct characters is \"bcdd\" with length 4."
        )

        input_format = (
            "Line 1: string s (0 <= len(s) <= 5 * 10^4)\n"
            "Line 2: integer k (0 <= k <= 26)"
        )

        output_format = "Single integer: length of longest substring with at most k distinct characters"

        constraints = (
            "0 <= s.length <= 5 * 10^4\n"
            "0 <= k <= 26\n"
            "s consists of English letters only."
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "lengthOfLongestSubstringKDistinct"
            problem.parameters = [
                {"name": "s", "type": "str"},
                {"name": "k", "type": "int"},
            ]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1300
            problem.is_active = True

            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception:
                logger.warning(
                    "Could not delete old test cases (referenced by submissions). "
                    "Keeping existing ones and updating metadata only."
                )
                await db.rollback()
                await db.refresh(problem)
        else:
            logger.info("Creating new problem entry.")
            problem = Problem(
                title=TITLE,
                description=description,
                difficulty=Difficulty.HARD,
                input_format=input_format,
                output_format=output_format,
                constraints=constraints,
                method_name="lengthOfLongestSubstringKDistinct",
                parameters=[
                    {"name": "s", "type": "str"},
                    {"name": "k", "type": "int"},
                ],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1300,
                is_active=True,
            )
            db.add(problem)
            await db.flush()
            test_cases_deleted = True

        if test_cases_deleted:
            test_cases = build_test_cases()
            for tc in test_cases:
                db.add(TestCase(problem_id=problem.id, **tc))
            await db.commit()
            logger.info("Seeded '%s' with %d test cases.", TITLE, len(test_cases))
        else:
            await db.commit()
            logger.info("Updated metadata for '%s'. Test cases kept from previous seeding.", TITLE)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
