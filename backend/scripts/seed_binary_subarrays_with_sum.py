"""
Seed script — insert/update 'Binary Subarrays With Sum'
with 300+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_binary_subarrays_with_sum
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

TITLE = "Binary Subarrays With Sum"


def num_subarrays_with_sum(nums: list[int], goal: int) -> int:
    """Reference solver using prefix sums + frequency map."""
    prefix = 0
    freq = {0: 1}
    count = 0

    for x in nums:
        prefix += x
        count += freq.get(prefix - goal, 0)
        freq[prefix] = freq.get(prefix, 0) + 1

    return count


def make_case(nums: list[int], goal: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(goal),
        "expected_output": json.dumps(num_subarrays_with_sum(nums, goal)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt samples.
    samples = [
        ([1, 1, 0, 1, 0, 0, 1], 3),
        ([0, 0, 0, 0, 1], 0),
    ]
    for nums, goal in samples:
        cases.append(make_case(nums, goal, idx, is_sample=True))
        idx += 1

    # Edge and boundary cases.
    edge_cases = [
        ([0], 0),
        ([1], 0),
        ([1], 1),
        ([0, 0], 0),
        ([1, 1], 2),
        ([1, 1], 1),
        ([0, 1], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 0], 0),
        ([0, 0, 0, 0], 0),
        ([1, 1, 1, 1], 0),
        ([1, 1, 1, 1], 2),
        ([1, 1, 1, 1], 4),
        ([1, 1, 1, 1], 5),
        ([0, 0, 0, 0, 0], 1),
        ([1, 0, 1, 0, 1], 2),
        ([1, 0, 1, 0, 1], 3),
        ([1, 0, 1, 0, 1], 0),
        ([0, 1, 0, 1, 0, 1, 0], 2),
        ([0, 1, 0, 1, 0, 1, 0], 1),
        ([0, 1, 0, 1, 0, 1, 0], 0),
    ]
    for nums, goal in edge_cases:
        cases.append(make_case(nums, goal, idx))
        idx += 1

    # Structured patterns.
    for n in [10, 20, 35, 50, 75, 100, 150, 220, 300, 500]:
        all_zero = [0] * n
        all_one = [1] * n
        alternating = [i % 2 for i in range(n)]
        blocks = ([0] * (n // 3)) + ([1] * (n // 3)) + ([0] * (n - 2 * (n // 3)))

        goals = [0, 1, 2, 3, 5, 10, n // 2, n, n + 1]
        for goal in goals:
            if goal >= 0:
                cases.append(make_case(all_zero, goal, idx)); idx += 1
                cases.append(make_case(all_one, goal, idx)); idx += 1
                cases.append(make_case(alternating, goal, idx)); idx += 1
                cases.append(make_case(blocks, goal, idx)); idx += 1

    # Deterministic randomized set to exceed 300 total.
    rng = random.Random(20260402)
    while len(cases) < 340:
        n = rng.randint(1, 900)
        mode = rng.randint(0, 4)

        if mode == 0:
            # Sparse ones.
            nums = [1 if rng.random() < 0.15 else 0 for _ in range(n)]
        elif mode == 1:
            # Dense ones.
            nums = [1 if rng.random() < 0.8 else 0 for _ in range(n)]
        elif mode == 2:
            # Balanced.
            nums = [1 if rng.random() < 0.5 else 0 for _ in range(n)]
        elif mode == 3:
            # Run-heavy.
            nums = []
            remaining = n
            bit = rng.randint(0, 1)
            while remaining > 0:
                run = min(remaining, rng.randint(1, 40))
                nums.extend([bit] * run)
                remaining -= run
                bit ^= 1
        else:
            # Alternating with occasional flips.
            nums = [i % 2 for i in range(n)]
            for _ in range(max(1, n // 20)):
                j = rng.randint(0, n - 1)
                nums[j] ^= 1

        ones = sum(nums)
        goal = rng.randint(0, max(0, min(n + 3, ones + rng.randint(0, 10))))
        cases.append(make_case(nums, goal, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given a binary array nums and an integer goal, return the number of non-empty subarrays "
            "with sum equal to goal.\n\n"
            "A subarray is a contiguous part of the array.\n\n"
            "Example 1\n"
            "Input: nums = [1,1,0,1,0,0,1], goal = 3\n"
            "Output: 4\n\n"
            "Example 2\n"
            "Input: nums = [0,0,0,0,1], goal = 0\n"
            "Output: 10"
        )

        input_format = (
            "Line 1: JSON array nums (binary int[])\n"
            "Line 2: integer goal"
        )
        output_format = "Single integer: number of non-empty subarrays whose sum equals goal"
        constraints = (
            "1 <= nums.length <= 3 * 10^4\n"
            "nums[i] is either 0 or 1\n"
            "0 <= goal <= nums.length"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "numSubarraysWithSum"
            problem.parameters = [
                {"name": "nums", "type": "int[]"},
                {"name": "goal", "type": "int"},
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
                method_name="numSubarraysWithSum",
                parameters=[
                    {"name": "nums", "type": "int[]"},
                    {"name": "goal", "type": "int"},
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
