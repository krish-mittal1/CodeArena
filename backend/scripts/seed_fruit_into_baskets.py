"""
Seed script — insert/update 'Fruit Into Baskets'
with 200+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_fruit_into_baskets
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

TITLE = "Fruit Into Baskets"


def total_fruit(fruits: list[int]) -> int:
    """Reference sliding-window solver: longest subarray with at most 2 distinct values."""
    left = 0
    counts: dict[int, int] = {}
    best = 0

    for right, fruit in enumerate(fruits):
        counts[fruit] = counts.get(fruit, 0) + 1

        while len(counts) > 2:
            lf = fruits[left]
            counts[lf] -= 1
            if counts[lf] == 0:
                del counts[lf]
            left += 1

        best = max(best, right - left + 1)

    return best


def make_case(fruits: list[int], order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(fruits),
        "expected_output": json.dumps(total_fruit(fruits)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Samples from prompt.
    samples = [
        [1, 2, 1],
        [1, 2, 3, 2, 2],
        [1, 2, 3, 4, 5],
    ]
    for arr in samples:
        cases.append(make_case(arr, idx, is_sample=True))
        idx += 1

    # Edge cases.
    edge_cases = [
        [0],
        [7, 7],
        [1, 2],
        [1, 2, 1, 2, 1, 2],
        [1, 2, 3],
        [3, 3, 3, 3, 3],
        [1, 2, 3, 1, 2, 3, 1, 2, 3],
        [1, 0, 1, 4, 1, 4, 1, 2, 3],
        [5, 5, 1, 1, 5, 5],
        [8, 9, 8, 9, 10],
        [10, 11, 12, 13, 14, 14, 14],
        [4, 5, 5, 5, 6, 6, 5, 5, 5, 4],
        [1, 2, 2, 2, 3, 3, 2, 2, 1],
        [1, 2, 1, 3, 4, 3, 5, 1, 2],
        [2, 2, 2, 1, 1, 1, 2, 2, 2],
        [1000000000, -1000000000, 1000000000, -1000000000],
    ]
    for arr in edge_cases:
        cases.append(make_case(arr, idx))
        idx += 1

    # Structured stress patterns.
    for n in [10, 25, 50, 75, 100, 150, 200]:
        alt = [1 if i % 2 == 0 else 2 for i in range(n)]
        blocks = ([1] * (n // 3)) + ([2] * (n // 3)) + ([3] * (n - 2 * (n // 3)))
        three_cycle = [(i % 3) + 1 for i in range(n)]
        boundary_break = ([1] * (n // 2)) + ([2] * (n // 2 - 1)) + [3]
        long_tail = [9] + ([8] * (n - 2)) + [7]

        for arr in [alt, blocks, three_cycle, boundary_break, long_tail]:
            cases.append(make_case(arr, idx))
            idx += 1

    # Deterministic randomized cases to reach 220+ cases total.
    rng = random.Random(20260330)
    while len(cases) < 220:
        n = rng.randint(1, 400)

        mode = rng.randint(0, 4)
        if mode == 0:
            # Low variety -> often full length valid windows.
            palette = [rng.randint(0, 5), rng.randint(6, 12)]
        elif mode == 1:
            # Medium variety.
            palette = [rng.randint(0, 20) for _ in range(3)]
        elif mode == 2:
            # High variety with occasional repeats.
            palette = [rng.randint(-50, 50) for _ in range(10)]
        elif mode == 3:
            # Monotonic style values.
            start = rng.randint(-100, 100)
            palette = [start + i for i in range(6)]
        else:
            # Sparse large values.
            palette = [rng.randint(-10**9, 10**9) for _ in range(4)]

        arr = [rng.choice(palette) for _ in range(n)]
        cases.append(make_case(arr, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "You are given an integer array fruits where fruits[i] is the type of fruit produced by the i-th tree. "
            "You have two baskets, and each basket can only hold one fruit type with unlimited quantity.\n\n"
            "Starting from any tree, move to the right and pick exactly one fruit from each visited tree. "
            "If the current fruit cannot fit in either basket, you must stop.\n\n"
            "Return the maximum number of fruits you can pick.\n\n"
            "Example 1\n"
            "Input: fruits = [1,2,1]\n"
            "Output: 3\n\n"
            "Example 2\n"
            "Input: fruits = [1,2,3,2,2]\n"
            "Output: 4\n\n"
            "Example 3\n"
            "Input: fruits = [1,2,3,4,5]\n"
            "Output: 2"
        )

        input_format = "Line 1: JSON array fruits (int[])"
        output_format = "Single integer: maximum fruits collectable with at most two fruit types"
        constraints = (
            "1 <= fruits.length <= 10^5\n"
            "0 <= fruits[i] <= 10^9"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.MEDIUM
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "totalFruit"
            problem.parameters = [{"name": "fruits", "type": "int[]"}]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1100
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
                method_name="totalFruit",
                parameters=[{"name": "fruits", "type": "int[]"}],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1100,
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
