"""
Seed script - insert/update 'Minimum Window Substring'
with 180+ test cases (samples + edge + deterministic randomized cases).

Usage:
    python -m backend.scripts.seed_minimum_window_substring
"""

import asyncio
import json
import logging
import random
from collections import Counter

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Minimum Window Substring"


def min_window(s: str, t: str) -> str:
    if not s or not t or len(t) > len(s):
        return ""

    need = Counter(t)
    missing = len(t)
    left = 0
    best_start = 0
    best_len = float("inf")

    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1

        while missing == 0:
            window_len = right - left + 1
            if window_len < best_len:
                best_len = window_len
                best_start = left

            left_ch = s[left]
            need[left_ch] += 1
            if need[left_ch] > 0:
                missing += 1
            left += 1

    if best_len == float("inf"):
        return ""
    return s[best_start:best_start + best_len]


def make_case(s: str, t: str, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s) + "\n" + json.dumps(t),
        "expected_output": json.dumps(min_window(s, t)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ("ADOBECODEBANC", "ABC"),
        ("a", "a"),
    ]
    for s, t in samples:
        cases.append(make_case(s, t, idx, True))
        idx += 1

    edge_cases = [
        ("a", "aa"),
        ("ab", "b"),
        ("ab", "a"),
        ("ab", "ab"),
        ("ab", "ba"),
        ("aa", "aa"),
        ("aaa", "aa"),
        ("aaflslflsldkalskaaa", "aaa"),
        ("bba", "ab"),
        ("bdab", "ab"),
        ("abc", "d"),
        ("abc", "ac"),
        ("cabefgecdaecf", "cae"),
        ("thisisateststring", "tist"),
        ("xyyzyzyx", "xyz"),
        ("aaaaaaaaaaaabbbbbcdd", "abcdd"),
        ("ABBBCZBAC", "ABC"),
        ("mississippi", "issi"),
    ]
    for s, t in edge_cases:
        cases.append(make_case(s, t, idx))
        idx += 1

    structured = [
        ("ABC" * 20, "ABC"),
        ("A" * 80 + "B" + "C", "ABC"),
        ("Z" * 40 + "ABC" + "Z" * 40, "ABC"),
        ("QWER" * 30 + "ABC" + "TYUI" * 10, "ABC"),
        ("ABBCCBAACCBBAA", "ABC"),
        ("a" * 100 + "b" * 50 + "c" * 30, "abc"),
        ("ab" * 60 + "c", "abc"),
        ("c" + "ba" * 60, "abc"),
    ]
    for s, t in structured:
        cases.append(make_case(s, t, idx))
        idx += 1

    for n in [20, 40, 80, 120]:
        s1 = "".join(chr(ord("A") + (i % 5)) for i in range(n))
        s2 = "".join(chr(ord("A") + ((i * 3) % 7)) for i in range(n))
        s3 = ("A" * (n // 3)) + ("B" * (n // 3)) + ("C" * (n - 2 * (n // 3)))
        for t in ["ABC", "AAB", "BCD", "ACE"]:
            cases.append(make_case(s1, t, idx)); idx += 1
            cases.append(make_case(s2, t, idx)); idx += 1
            cases.append(make_case(s3, t, idx)); idx += 1

    rng = random.Random(20260331)
    alphabet = "ABCDEabcde"
    while len(cases) < 190:
        s_len = rng.randint(1, 180)
        t_len = rng.randint(1, min(8, s_len))
        s = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(s_len))
        t = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(t_len))
        cases.append(make_case(s, t, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given two strings s and t, return the smallest substring of s that contains every character "
            "from t, including duplicates. If no such substring exists, return an empty string.\n\n"
            "Example 1\n"
            "Input: s = \"ADOBECODEBANC\", t = \"ABC\"\n"
            "Output: \"BANC\"\n\n"
            "Example 2\n"
            "Input: s = \"a\", t = \"a\"\n"
            "Output: \"a\""
        )

        input_format = (
            "Line 1: JSON string s\n"
            "Line 2: JSON string t"
        )
        output_format = "JSON string: the minimum window in s containing all characters of t"
        constraints = (
            "1 <= s.length <= 10^5\n"
            "1 <= t.length <= 10^5\n"
            "s and t consist of English letters"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "minWindow"
            problem.parameters = [
                {"name": "s", "type": "str"},
                {"name": "t", "type": "str"},
            ]
            problem.return_type = "str"
            problem.time_limit_ms = 2500
            problem.memory_limit_mb = 256
            problem.rating = 1500
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
                method_name="minWindow",
                parameters=[
                    {"name": "s", "type": "str"},
                    {"name": "t", "type": "str"},
                ],
                return_type="str",
                time_limit_ms=2500,
                memory_limit_mb=256,
                rating=1500,
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
