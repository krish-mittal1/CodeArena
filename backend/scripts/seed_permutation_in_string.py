"""
Seed script - insert/update 'Permutation in String'
with 170+ test cases (samples + edge + deterministic randomized cases).

Usage:
    python -m backend.scripts.seed_permutation_in_string
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

TITLE = "Permutation in String"


def check_inclusion(s1: str, s2: str) -> bool:
    n1 = len(s1)
    n2 = len(s2)
    if n1 > n2:
        return False

    need = Counter(s1)
    window = Counter(s2[:n1])
    if window == need:
        return True

    for i in range(n1, n2):
        add_ch = s2[i]
        rem_ch = s2[i - n1]
        window[add_ch] += 1
        window[rem_ch] -= 1
        if window[rem_ch] == 0:
            del window[rem_ch]
        if window == need:
            return True

    return False


def make_case(s1: str, s2: str, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s1) + "\n" + json.dumps(s2),
        "expected_output": json.dumps(check_inclusion(s1, s2)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ("ab", "eidbaooo"),
        ("ab", "eidboaoo"),
    ]
    for s1, s2 in samples:
        cases.append(make_case(s1, s2, idx, True))
        idx += 1

    edge_cases = [
        ("a", "a"),
        ("a", "b"),
        ("abc", "bbbca"),
        ("abc", "ccccbbbbaaaa"),
        ("adc", "dcda"),
        ("hello", "ooolleoooleh"),
        ("xyz", "afdgzyxksldfm"),
        ("aa", "eidbaaoo"),
        ("aaa", "aaaaaa"),
        ("abcd", "abc"),
        ("ab", "ab"),
        ("ab", "ba"),
        ("abc", "cab"),
        ("abc", "defghijkl"),
        ("zz", "zzzz"),
        ("pq", "qpqpqp"),
        ("long", "gnol"),
        ("abba", "eidbaabboo"),
    ]
    for s1, s2 in edge_cases:
        cases.append(make_case(s1, s2, idx))
        idx += 1

    for n in [20, 40, 80, 120, 200]:
        source = "".join(chr(ord("a") + (i % 5)) for i in range(n))
        alt = "".join(chr(ord("a") + ((i * 3) % 7)) for i in range(n))
        cases.append(make_case("abc", source, idx)); idx += 1
        cases.append(make_case("aab", source, idx)); idx += 1
        cases.append(make_case("bca", alt, idx)); idx += 1
        cases.append(make_case("xyz", alt, idx)); idx += 1

    rng = random.Random(20260331)
    alphabet = "abcde"
    while len(cases) < 180:
        len1 = rng.randint(1, 8)
        len2 = rng.randint(len1, 180)
        s1 = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(len1))
        s2 = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(len2))
        cases.append(make_case(s1, s2, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given two strings s1 and s2, return true if some permutation of s1 appears as a contiguous "
            "substring of s2. Otherwise return false.\n\n"
            "Example 1\n"
            "Input: s1 = \"ab\", s2 = \"eidbaooo\"\n"
            "Output: true\n\n"
            "Example 2\n"
            "Input: s1 = \"ab\", s2 = \"eidboaoo\"\n"
            "Output: false"
        )

        input_format = (
            "Line 1: JSON string s1\n"
            "Line 2: JSON string s2"
        )
        output_format = "Boolean: true if a permutation of s1 appears in s2, else false"
        constraints = (
            "1 <= s1.length <= 10^4\n"
            "1 <= s2.length <= 10^4\n"
            "s1 and s2 consist of lowercase English letters"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.MEDIUM
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "checkInclusion"
            problem.parameters = [
                {"name": "s1", "type": "str"},
                {"name": "s2", "type": "str"},
            ]
            problem.return_type = "bool"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1200
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
                difficulty=Difficulty.MEDIUM,
                input_format=input_format,
                output_format=output_format,
                constraints=constraints,
                method_name="checkInclusion",
                parameters=[
                    {"name": "s1", "type": "str"},
                    {"name": "s2", "type": "str"},
                ],
                return_type="bool",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1200,
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
