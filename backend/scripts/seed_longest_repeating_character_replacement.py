"""
Seed script — insert/update 'Longest Repeating Character Replacement'
with 300+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_longest_repeating_character_replacement
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

TITLE = "Longest Repeating Character Replacement"


def character_replacement(s: str, k: int) -> int:
    """Reference sliding-window solver."""
    if not s:
        return 0
    if k <= 0:
        best = 1
        run = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                run += 1
            else:
                run = 1
            if run > best:
                best = run
        return best

    left = 0
    best = 0
    max_freq = 0
    counts: dict[str, int] = {}

    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        if counts[ch] > max_freq:
            max_freq = counts[ch]

        while (right - left + 1) - max_freq > k:
            lc = s[left]
            counts[lc] -= 1
            left += 1

        window_len = right - left + 1
        if window_len > best:
            best = window_len

    return best


def make_case(s: str, k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s) + "\n" + json.dumps(k),
        "expected_output": json.dumps(character_replacement(s, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt samples.
    samples = [
        ("BAABAABBBAAA", 2),
        ("AABABBA", 1),
    ]
    for s, k in samples:
        cases.append(make_case(s, k, idx, is_sample=True))
        idx += 1

    # Edge and boundary cases.
    edge_cases = [
        ("A", 0),
        ("A", 1),
        ("AA", 0),
        ("AA", 1),
        ("AB", 0),
        ("AB", 1),
        ("AB", 2),
        ("ABA", 0),
        ("ABA", 1),
        ("ABA", 2),
        ("ABAB", 1),
        ("ABAB", 2),
        ("ABCDE", 0),
        ("ABCDE", 1),
        ("ABCDE", 2),
        ("ABCDE", 5),
        ("AAAAA", 0),
        ("AAAAA", 2),
        ("BAAAAB", 1),
        ("BAAAAB", 2),
        ("ZZXYZZ", 1),
        ("ZZXYZZ", 2),
        ("XYZXYZXYZ", 1),
        ("XYZXYZXYZ", 3),
        ("BBBBBA", 0),
        ("BBBBBA", 1),
        ("ABBBBC", 1),
        ("ABBBBC", 2),
        ("QWERTYUIOP", 3),
        ("AAAAAAAAAAB", 1),
        ("ABCDDDDDDD", 2),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 0),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 5),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 25),
    ]
    for s, k in edge_cases:
        cases.append(make_case(s, k, idx))
        idx += 1

    # Structured patterns.
    for n in [12, 24, 48, 72, 96, 128, 160, 220]:
        two_alt = "".join("AB"[i % 2] for i in range(n))
        three_alt = "".join("ABC"[i % 3] for i in range(n))
        blocks = ("A" * (n // 4)) + ("B" * (n // 4)) + ("C" * (n // 4)) + ("D" * (n - 3 * (n // 4)))
        near_uniform = ("A" * (n - 3)) + "BCD"

        for k in [0, 1, 2, 3, 5, 10]:
            if k <= n:
                cases.append(make_case(two_alt, k, idx)); idx += 1
                cases.append(make_case(three_alt, k, idx)); idx += 1
                cases.append(make_case(blocks, k, idx)); idx += 1
                cases.append(make_case(near_uniform, k, idx)); idx += 1

    # Alphabet sweep patterns.
    for repeat in [2, 3, 4, 6, 8]:
        s = "".join(chr(ord("A") + (i % 26)) for i in range(26 * repeat))
        for k in [0, 1, 2, 4, 8, 13, 20]:
            cases.append(make_case(s, k, idx))
            idx += 1

    # Deterministic randomized cases to exceed 300 cases.
    rng = random.Random(20260331)
    while len(cases) < 320:
        n = rng.randint(1, 500)
        k = rng.randint(0, min(30, n))

        mode = rng.randint(0, 4)
        if mode == 0:
            # Low variety, long runs.
            alphabet = "AB"
        elif mode == 1:
            alphabet = "ABC"
        elif mode == 2:
            alphabet = "ABCDE"
        elif mode == 3:
            alphabet = "ABCDEFGHIJ"
        else:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        s_chars = [alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(n)]
        s = "".join(s_chars)
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
            "Given a string s consisting of uppercase English letters and an integer k, you may choose "
            "any character and change it to any other uppercase English letter at most k times.\n\n"
            "Return the length of the longest substring that can contain only one repeating letter "
            "after performing at most k replacements.\n\n"
            "Example 1\n"
            "Input: s = \"BAABAABBBAAA\", k = 2\n"
            "Output: 6\n\n"
            "Example 2\n"
            "Input: s = \"AABABBA\", k = 1\n"
            "Output: 4"
        )

        input_format = (
            "Line 1: JSON string s\n"
            "Line 2: integer k"
        )
        output_format = "Single integer: maximum length of a repeating-character substring after at most k replacements"
        constraints = (
            "1 <= s.length <= 10^5\n"
            "0 <= k <= s.length\n"
            "s consists of uppercase English letters"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "characterReplacement"
            problem.parameters = [
                {"name": "s", "type": "str"},
                {"name": "k", "type": "int"},
            ]
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
                method_name="characterReplacement",
                parameters=[
                    {"name": "s", "type": "str"},
                    {"name": "k", "type": "int"},
                ],
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
