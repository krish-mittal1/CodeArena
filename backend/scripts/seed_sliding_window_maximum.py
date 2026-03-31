"""
Seed script - insert/update 'Sliding Window Maximum'
with 180+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_sliding_window_maximum
"""

import asyncio
import json
import logging
import random
from collections import deque

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Sliding Window Maximum"


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    if not nums or k <= 0:
        return []
    if k == 1:
        return nums[:]

    dq: deque[int] = deque()
    result: list[int] = []

    for i, value in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] <= value:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


def make_case(nums: list[int], k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(k),
        "expected_output": json.dumps(max_sliding_window(nums, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3),
        ([1], 1),
    ]
    for nums, k in samples:
        cases.append(make_case(nums, k, idx, True))
        idx += 1

    edge_cases = [
        ([9], 1),
        ([1, -1], 1),
        ([1, -1], 2),
        ([4, 4, 4, 4], 2),
        ([-5, -2, -9, -1], 2),
        ([10, 9, 8, 7, 6], 3),
        ([1, 2, 3, 4, 5], 3),
        ([5, 4, 3, 2, 1], 5),
        ([2, 1, 2, 1, 2, 1], 2),
        ([7, 2, 4], 2),
        ([0, 0, 0, 0], 3),
        ([100000, -100000, 99999, -99999], 2),
        ([1, 3, 1, 2, 0, 5], 3),
        ([8, 7, 6, 9], 1),
        ([8, 7, 6, 9], 4),
    ]
    for nums, k in edge_cases:
        cases.append(make_case(nums, k, idx))
        idx += 1

    for n in [10, 20, 40, 80, 120, 200]:
        inc = list(range(n))
        dec = list(range(n, 0, -1))
        alt = [100 if i % 2 == 0 else -100 for i in range(n)]
        blocks = ([1] * (n // 3)) + ([5] * (n // 3)) + ([2] * (n - 2 * (n // 3)))
        for k in [1, 2, 3, 5, n // 2, n]:
            cases.append(make_case(inc, k, idx)); idx += 1
            cases.append(make_case(dec, k, idx)); idx += 1
            cases.append(make_case(alt, k, idx)); idx += 1
            cases.append(make_case(blocks, k, idx)); idx += 1

    rng = random.Random(20260331)
    while len(cases) < 200:
        n = rng.randint(1, 300)
        nums = [rng.randint(-10**4, 10**4) for _ in range(n)]
        k = rng.randint(1, n)
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
            "Given an integer array nums and an integer k, move a window of size k "
            "from left to right across the array and report the maximum value in each window.\n\n"
            "Return the list of window maximums in order.\n\n"
            "Example 1\n"
            "Input: nums = [1,3,-1,-3,5,3,6,7], k = 3\n"
            "Output: [3,3,5,5,6,7]\n\n"
            "Example 2\n"
            "Input: nums = [1], k = 1\n"
            "Output: [1]"
        )

        input_format = (
            "Line 1: JSON array nums (int[])\n"
            "Line 2: integer k"
        )
        output_format = "JSON array of integers: maximum value for each contiguous window of size k"
        constraints = (
            "1 <= nums.length <= 10^5\n"
            "-10^4 <= nums[i] <= 10^4\n"
            "1 <= k <= nums.length"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.HARD
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "maxSlidingWindow"
            problem.parameters = [
                {"name": "nums", "type": "int[]"},
                {"name": "k", "type": "int"},
            ]
            problem.return_type = "int[]"
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
                method_name="maxSlidingWindow",
                parameters=[
                    {"name": "nums", "type": "int[]"},
                    {"name": "k", "type": "int"},
                ],
                return_type="int[]",
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
