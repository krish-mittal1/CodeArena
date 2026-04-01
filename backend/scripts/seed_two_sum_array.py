import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Two Sum"
TARGET_CASES = 601


def solve(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for idx, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], idx]
        seen[value] = idx
    return []


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([2, 7, 11, 15], 9),
        ([3, 2, 4], 6),
        ([3, 3], 6),
    ]
    for nums, target in samples:
        cases.append(make_case(nums, target, expected_output=solve(nums, target), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([0, 4, 3, 0], 0),
        ([-3, 4, 3, 90], 0),
        ([1, 5, 1, 5], 10),
        ([1000000, -1000000], 0),
        ([8, 1, 6, 3, 5, 7], 13),
        ([9, -2, 11, 4, -7], 2),
        ([1, 2], 3),
        ([50, -20, 70, 10], 80),
    ]
    for nums, target in fixed:
        cases.append(make_case(nums, target, expected_output=solve(nums, target), idx=idx))
        idx += 1

    rng = random.Random(2026040201)
    while len(cases) < TARGET_CASES:
        n = rng.randint(2, 220)
        nums = [rng.randint(-10**6, 10**6) for _ in range(n)]
        i = rng.randrange(n)
        j = rng.randrange(n)
        while j == i:
            j = rng.randrange(n)
        target = nums[i] + nums[j]
        cases.append(make_case(nums, target, expected_output=solve(nums, target), idx=idx))
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
                description="Given an array of integers nums and an integer target, return the indices of the two numbers such that they add up to target.\n\nYou may assume that each input has exactly one solution, and you may not use the same element twice.\nReturn the answer in any order.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: JSON array nums\nLine 2: integer target",
                output_format="JSON array of two indices",
                constraints="2 <= nums.length <= 220\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nExactly one valid answer exists.",
                method_name="twoSum",
                parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
                return_type="int[]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=900,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
