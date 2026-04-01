import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Find Minimum in Rotated Sorted Array"
TARGET_CASES = 541


def solve(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]


def rotate(arr: list[int], k: int) -> list[int]:
    if not arr:
        return arr
    k %= len(arr)
    return arr[k:] + arr[:k]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [[3, 4, 5, 1, 2], [4, 5, 6, 7, 0, 1, 2], [11, 13, 15, 17]]
    for nums in samples:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [2, 1],
        [5, 1, 2, 3, 4],
        [2, 3, 4, 5, 1],
        [-4, -3, -2, -1, -8, -7, -6, -5],
        [30, 40, 50, 10, 20],
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040203)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 260)
        start = rng.randint(-10**6, 10**6)
        step = rng.randint(1, 10)
        arr = [start + step * i for i in range(n)]
        nums = rotate(arr, rng.randint(0, n - 1))
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
                description="Suppose an array of distinct integers is sorted in ascending order and rotated between 1 and n times. Return the minimum element in the array.\n\nYou must write an algorithm that runs in O(log n) time.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums",
                output_format="Single integer: the minimum element",
                constraints="1 <= nums.length <= 5000\n-10^9 <= nums[i] <= 10^9\nAll integers are unique.\nnums is sorted and rotated.",
                method_name="findMin",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1150,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
