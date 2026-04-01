import asyncio
import bisect
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Find First and Last Position of Element in Sorted Array"
TARGET_CASES = 556


def solve(nums: list[int], target: int) -> list[int]:
    left = bisect.bisect_left(nums, target)
    right = bisect.bisect_right(nums, target) - 1
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, right]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([5, 7, 7, 8, 8, 10], 8),
        ([5, 7, 7, 8, 8, 10], 6),
        ([], 0),
    ]
    for nums, target in samples:
        cases.append(make_case(nums, target, expected_output=solve(nums, target), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 1),
        ([1], 0),
        ([2, 2], 2),
        ([1, 2, 3, 4, 5], 1),
        ([1, 2, 3, 4, 5], 5),
        ([1, 1, 1, 1, 1], 1),
        ([1, 2, 2, 2, 3, 4], 2),
        ([-3, -3, -2, -1, -1, 0], -1),
    ]
    for nums, target in fixed:
        cases.append(make_case(nums, target, expected_output=solve(nums, target), idx=idx))
        idx += 1

    rng = random.Random(2026040204)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 260)
        nums = sorted(rng.randint(-1000, 1000) for _ in range(n))
        if nums and rng.random() < 0.7:
            target = nums[rng.randrange(len(nums))]
        else:
            target = rng.randint(-1100, 1100)
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
                description="Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.\n\nIf target is not found in the array, return [-1, -1].\n\nYou must write an algorithm with O(log n) runtime complexity.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums\nLine 2: integer target",
                output_format="JSON array [firstIndex, lastIndex]",
                constraints="0 <= nums.length <= 10^5\n-10^9 <= nums[i], target <= 10^9\nnums is sorted in non-decreasing order.",
                method_name="searchRange",
                parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
                return_type="int[]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
