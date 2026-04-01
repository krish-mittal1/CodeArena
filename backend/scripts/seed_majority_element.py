import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Majority Element"
TARGET_CASES = 548


def solve(nums: list[int]) -> int:
    candidate = None
    count = 0
    for value in nums:
        if count == 0:
            candidate = value
        count += 1 if value == candidate else -1
    return candidate


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for nums in ([3, 2, 3], [2, 2, 1, 1, 1, 2, 2], [1]):
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1, 1],
        [-1, -1, -1, 2, 3],
        [0, 0, 0, 1, 2],
        [9, 8, 9, 8, 9],
        [5, 5, 5, 5, 4, 4, 4],
        [1000000, 1000000, -1000000],
        [7, 6, 7, 6, 7, 6, 7],
        [4, 4, 4, 2, 4, 3, 4, 1, 4],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040205)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 401)
        majority = rng.randint(-10**9, 10**9)
        majority_count = (n // 2) + 1 + rng.randint(0, max(0, n - (n // 2) - 1))
        nums = [majority] * majority_count
        while len(nums) < n:
            value = rng.randint(-10**9, 10**9)
            if value != majority:
                nums.append(value)
        rng.shuffle(nums)
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        await upsert_problem(
            db,
            TITLE,
            dict(
                description="Given an array nums of size n, return the majority element.\n\nThe majority element is the element that appears more than ⌊n / 2⌋ times. You may assume that the majority element always exists in the array.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: JSON array nums",
                output_format="Single integer: majority element",
                constraints="1 <= nums.length <= 401\n-10^9 <= nums[i] <= 10^9",
                method_name="majorityElement",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=950,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
