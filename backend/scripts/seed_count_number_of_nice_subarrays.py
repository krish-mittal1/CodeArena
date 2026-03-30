"""
Seed script — insert/update 'Count number of Nice subarrays'
with 500+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_count_number_of_nice_subarrays
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

TITLE = "Count number of Nice subarrays"


def count_nice_subarrays(nums: list[int], k: int) -> int:
    """Reference solver: prefix count of odd numbers."""
    odd_prefix = 0
    freq = {0: 1}
    total = 0

    for x in nums:
        odd_prefix += (x & 1)
        total += freq.get(odd_prefix - k, 0)
        freq[odd_prefix] = freq.get(odd_prefix, 0) + 1

    return total


def make_case(nums: list[int], k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(k),
        "expected_output": json.dumps(count_nice_subarrays(nums, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt samples.
    samples = [
        ([1, 1, 2, 1, 1], 3),
        ([4, 8, 2], 1),
    ]
    for nums, k in samples:
        cases.append(make_case(nums, k, idx, is_sample=True))
        idx += 1

    # Edge and boundary cases.
    edge_cases = [
        ([1], 1),
        ([2], 1),
        ([1, 3], 1),
        ([1, 3], 2),
        ([2, 4], 1),
        ([2, 4, 6], 1),
        ([2, 4, 6], 2),
        ([1, 2, 3], 1),
        ([1, 2, 3], 2),
        ([1, 2, 3], 3),
        ([1, 1, 1, 1], 1),
        ([1, 1, 1, 1], 2),
        ([1, 1, 1, 1], 3),
        ([1, 1, 1, 1], 4),
        ([1, 1, 1, 1], 5),
        ([2, 2, 2, 2], 1),
        ([2, 2, 2, 2], 3),
        ([1, 2, 1, 2, 1], 1),
        ([1, 2, 1, 2, 1], 2),
        ([1, 2, 1, 2, 1], 3),
        ([1, 2, 1, 2, 1], 4),
        ([9, 8, 7, 6, 5, 4, 3, 2, 1], 3),
        ([100, 101, 102, 103, 104], 2),
    ]
    for nums, k in edge_cases:
        cases.append(make_case(nums, k, idx))
        idx += 1

    # Structured patterns.
    for n in [10, 20, 30, 50, 75, 100, 150, 220, 300, 500]:
        all_even = [2] * n
        all_odd = [1] * n
        alternating = [1 if i % 2 == 0 else 2 for i in range(n)]
        blocks = ([2] * (n // 3)) + ([1] * (n // 3)) + ([2] * (n - 2 * (n // 3)))

        for k in [1, 2, 3, 5, 10, n // 2, n, n + 1]:
            if k >= 1:
                cases.append(make_case(all_even, k, idx)); idx += 1
                cases.append(make_case(all_odd, k, idx)); idx += 1
                cases.append(make_case(alternating, k, idx)); idx += 1
                cases.append(make_case(blocks, k, idx)); idx += 1

    # Deterministic randomized set to exceed 500 total.
    rng = random.Random(20260403)
    while len(cases) < 560:
        n = rng.randint(1, 1000)
        mode = rng.randint(0, 4)

        if mode == 0:
            # Mostly even values.
            nums = [rng.choice([2, 4, 6, 8, 10, 11]) for _ in range(n)]
        elif mode == 1:
            # Mostly odd values.
            nums = [rng.choice([1, 3, 5, 7, 9, 10]) for _ in range(n)]
        elif mode == 2:
            # Balanced random values.
            nums = [rng.randint(1, 1000) for _ in range(n)]
        elif mode == 3:
            # Run-heavy parity segments.
            nums = []
            remaining = n
            odd_run = bool(rng.randint(0, 1))
            while remaining > 0:
                run = min(remaining, rng.randint(1, 45))
                if odd_run:
                    nums.extend([rng.choice([1, 3, 5, 7, 9])] * run)
                else:
                    nums.extend([rng.choice([2, 4, 6, 8, 10])] * run)
                remaining -= run
                odd_run = not odd_run
        else:
            # Alternating parity with occasional noise.
            nums = [1 if i % 2 == 0 else 2 for i in range(n)]
            for _ in range(max(1, n // 30)):
                j = rng.randint(0, n - 1)
                nums[j] = rng.randint(1, 99)

        odd_count = sum(x & 1 for x in nums)
        k = rng.randint(1, max(1, min(n + 3, odd_count + rng.randint(0, 12))))
        cases.append(make_case(nums, k, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given an integer array nums and an integer k, return the number of contiguous subarrays "
            "that contain exactly k odd numbers.\n\n"
            "Example 1\n"
            "Input: nums = [1,1,2,1,1], k = 3\n"
            "Output: 2\n\n"
            "Example 2\n"
            "Input: nums = [4,8,2], k = 1\n"
            "Output: 0"
        )

        input_format = (
            "Line 1: JSON array nums (int[])\n"
            "Line 2: integer k"
        )
        output_format = "Single integer: count of subarrays containing exactly k odd numbers"
        constraints = (
            "1 <= nums.length <= 5 * 10^4\n"
            "1 <= nums[i] <= 10^5\n"
            "1 <= k <= nums.length"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "numberOfSubarrays"
            problem.parameters = [
                {"name": "nums", "type": "int[]"},
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
                method_name="numberOfSubarrays",
                parameters=[
                    {"name": "nums", "type": "int[]"},
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
