"""
Seed script — insert/update 'Max Consecutive Ones III'
with 200+ test cases (samples + edge + randomized).

Usage:
    python -m backend.scripts.seed_max_consecutive_ones_iii
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

TITLE = "Max Consecutive Ones III"


def longest_ones(nums: list[int], k: int) -> int:
    """Reference solution using sliding window with zero budget."""
    left = 0
    zeros = 0
    best = 0

    for right, value in enumerate(nums):
        if value == 0:
            zeros += 1

        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


def make_case(nums: list[int], k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(k),
        "expected_output": json.dumps(longest_ones(nums, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Samples from prompt.
    cases.append(make_case([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 3, idx, is_sample=True)); idx += 1
    cases.append(make_case([0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1], 3, idx, is_sample=True)); idx += 1
    cases.append(make_case([1, 1, 0, 0, 1], 3, idx, is_sample=True)); idx += 1

    # Edge cases.
    edge_cases = [
        ([1], 0),
        ([1], 1),
        ([0], 0),
        ([0], 1),
        ([1, 1, 1, 1], 0),
        ([0, 0, 0, 0], 0),
        ([0, 0, 0, 0], 4),
        ([1, 0], 0),
        ([1, 0], 1),
        ([0, 1], 0),
        ([0, 1], 1),
        ([1, 0, 1, 0, 1], 0),
        ([1, 0, 1, 0, 1], 1),
        ([1, 0, 1, 0, 1], 2),
        ([1, 0, 1, 0, 1], 5),
        ([0, 1, 0, 1, 0, 1, 0], 2),
        ([1] * 50, 0),
        ([0] * 50, 0),
        ([0] * 50, 50),
        ([1] * 49 + [0], 0),
        ([0] + [1] * 49, 0),
        ([0] + [1] * 49, 1),
        ([1] * 25 + [0] * 25, 5),
        ([0] * 25 + [1] * 25, 5),
        ([1, 0] * 40, 10),
        ([0, 1] * 40, 10),
        ([1, 1, 1, 0, 0, 1, 1, 1, 0, 1], 2),
    ]
    for nums, k in edge_cases:
        cases.append(make_case(nums, k, idx)); idx += 1

    # Structured patterns to stress window behavior around dense zero clusters.
    for n in [10, 20, 35, 50, 75, 100]:
        all_ones = [1] * n
        all_zeros = [0] * n
        alternating = [1 if i % 2 == 0 else 0 for i in range(n)]
        blocks = ([1] * (n // 3)) + ([0] * (n // 3)) + ([1] * (n - 2 * (n // 3)))

        for k in [0, 1, 2, n // 5, n // 2, n]:
            cases.append(make_case(all_ones, k, idx)); idx += 1
            cases.append(make_case(all_zeros, k, idx)); idx += 1
            cases.append(make_case(alternating, k, idx)); idx += 1
            cases.append(make_case(blocks, k, idx)); idx += 1

    # Deterministic random cases to exceed 200.
    random.seed(20260329)
    while len(cases) < 220:
        n = random.randint(1, 500)
        p_zero = random.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        nums = [0 if random.random() < p_zero else 1 for _ in range(n)]
        k = random.randint(0, n)
        cases.append(make_case(nums, k, idx)); idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given a binary array nums and an integer k, flip at most k 0's.\n\n"
            "Return the maximum number of consecutive 1's after performing the flipping operation.\n\n"
            "Example 1\n"
            "Input: nums = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], k = 3\n"
            "Output: 10\n"
            "Explanation: Flip 0's at indices 3, 4, 5 to get ten consecutive 1's.\n\n"
            "Example 2\n"
            "Input: nums = [0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1], k = 3\n"
            "Output: 9\n\n"
            "Example 3\n"
            "Input: nums = [1, 1, 0, 0, 1], k = 3\n"
            "Output: 5"
        )

        input_format = (
            "Line 1: JSON array nums (int[] containing only 0/1)\n"
            "Line 2: integer k"
        )

        constraints = (
            "1 <= nums.length <= 10^5\n"
            "nums[i] is either 0 or 1\n"
            "0 <= k <= nums.length"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.MEDIUM
            problem.input_format = input_format
            problem.output_format = "Single integer: maximum consecutive ones after at most k flips"
            problem.constraints = constraints
            problem.method_name = "longestOnes"
            problem.parameters = [
                {"name": "nums", "type": "int[]"},
                {"name": "k", "type": "int"},
            ]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1150
            problem.is_active = True

            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception:
                logger.warning("Could not delete old test cases (referenced by submissions). Keeping existing ones and updating metadata only.")
                await db.rollback()
                await db.refresh(problem)
        else:
            logger.info("Creating new problem entry.")
            problem = Problem(
                title=TITLE,
                description=description,
                difficulty=Difficulty.MEDIUM,
                input_format=input_format,
                output_format="Single integer: maximum consecutive ones after at most k flips",
                constraints=constraints,
                method_name="longestOnes",
                parameters=[
                    {"name": "nums", "type": "int[]"},
                    {"name": "k", "type": "int"},
                ],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1150,
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
