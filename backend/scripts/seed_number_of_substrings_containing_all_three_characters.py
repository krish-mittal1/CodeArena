"""
Seed script — insert/update 'Number of Substrings Containing All Three Characters'
with 400+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_number_of_substrings_containing_all_three_characters
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

TITLE = "Number of Substrings Containing All Three Characters"


def count_substrings_all_three(s: str) -> int:
    """Reference O(n) sliding-window solver for alphabet {'a','b','c'}."""
    n = len(s)
    if n < 3:
        return 0

    left = 0
    counts = {"a": 0, "b": 0, "c": 0}
    total = 0

    for right, ch in enumerate(s):
        counts[ch] += 1

        while counts["a"] > 0 and counts["b"] > 0 and counts["c"] > 0:
            total += n - right
            counts[s[left]] -= 1
            left += 1

    return total


def make_case(s: str, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s),
        "expected_output": json.dumps(count_substrings_all_three(s)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Samples from prompt.
    samples = [
        "abcba",
        "ccabcc",
    ]
    for s in samples:
        cases.append(make_case(s, idx, is_sample=True))
        idx += 1

    # Explicit edge/boundary cases.
    edge_cases = [
        "a", "b", "c",
        "aa", "bb", "cc",
        "ab", "bc", "ca",
        "abc", "acb", "bac", "bca", "cab", "cba",
        "aaaaa", "bbbbb", "ccccc",
        "aabb", "bbcc", "ccaa",
        "aabbcc", "abcabc", "abccba",
        "aaabbbccc", "cccbbbaaa",
        "abca", "cabc", "bcab",
        "aaabc", "abccc", "ccaba",
        "abc" * 10,
        "a" * 30 + "b" * 30 + "c" * 30,
        "c" * 20 + "a" * 20 + "b" * 20,
        "ab" * 40 + "c",
        "ac" * 40 + "b",
        "bc" * 40 + "a",
    ]
    for s in edge_cases:
        cases.append(make_case(s, idx))
        idx += 1

    # Patterned stress cases.
    for n in [12, 24, 36, 48, 60, 75, 90, 120, 150, 200, 300, 500]:
        # Repeating cycle
        cyc = "".join("abc"[i % 3] for i in range(n))
        # Two-char heavy + one char tail
        aab_tail = ("ab" * (n // 2)) + "c"
        # Blocky
        blocks = ("a" * (n // 3)) + ("b" * (n // 3)) + ("c" * (n - 2 * (n // 3)))
        # Reverse blocks
        rev_blocks = ("c" * (n // 3)) + ("b" * (n // 3)) + ("a" * (n - 2 * (n // 3)))
        # Dominant single char with sparse others
        sparse = ("a" * max(1, n - 4)) + "bcab"

        for s in [cyc, aab_tail[:n], blocks, rev_blocks, sparse[:n]]:
            cases.append(make_case(s, idx))
            idx += 1

    # Deterministic random cases to exceed 400 total.
    rng = random.Random(20260401)
    while len(cases) < 430:
        n = rng.randint(1, 800)
        mode = rng.randint(0, 4)

        if mode == 0:
            # Uniform random over abc
            s = "".join("abc"[rng.randint(0, 2)] for _ in range(n))
        elif mode == 1:
            # Biased toward 'a'
            s = "".join(rng.choice(["a", "a", "a", "b", "c"]) for _ in range(n))
        elif mode == 2:
            # Biased toward 'b'
            s = "".join(rng.choice(["b", "b", "b", "a", "c"]) for _ in range(n))
        elif mode == 3:
            # Biased toward 'c'
            s = "".join(rng.choice(["c", "c", "c", "a", "b"]) for _ in range(n))
        else:
            # Construct runs
            runs = []
            remaining = n
            while remaining > 0:
                ch = "abc"[rng.randint(0, 2)]
                run_len = min(remaining, rng.randint(1, 30))
                runs.append(ch * run_len)
                remaining -= run_len
            s = "".join(runs)

        cases.append(make_case(s, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given a string s consisting only of characters 'a', 'b', and 'c', "
            "return the number of substrings that contain at least one occurrence "
            "of each character.\n\n"
            "Example 1\n"
            "Input: s = \"abcba\"\n"
            "Output: 5\n\n"
            "Example 2\n"
            "Input: s = \"ccabcc\"\n"
            "Output: 8"
        )

        input_format = "Line 1: JSON string s (only lowercase 'a', 'b', 'c')"
        output_format = "Single integer: count of substrings containing at least one 'a', one 'b', and one 'c'"
        constraints = (
            "1 <= s.length <= 10^5\n"
            "s[i] is one of {'a', 'b', 'c'}"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "numberOfSubstrings"
            problem.parameters = [{"name": "s", "type": "str"}]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1400
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
                method_name="numberOfSubstrings",
                parameters=[{"name": "s", "type": "str"}],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1400,
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
