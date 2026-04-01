import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Single Element in a Sorted Array"
TARGET_CASES = 562


def solve(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            left = mid + 2
        else:
            right = mid
    return nums[left]


def build_array(pairs: int, single: int) -> list[int]:
    values = []
    for i in range(pairs):
        base = i * 3
        values.extend([base, base])
    values.append(single)
    values.sort()
    return values


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [[1, 1, 2, 3, 3, 4, 4, 8, 8], [3, 3, 7, 7, 10, 11, 11]]
    for nums in samples:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [0, 1, 1],
        [1, 1, 2],
        [1, 1, 2, 3, 3],
        [1, 1, 2, 2, 3],
        [-5, -5, -2, -2, 4, 7, 7],
        [2, 2, 3, 3, 9, 10, 10],
        [4, 4, 6, 8, 8, 9, 9],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040207)
    while len(cases) < TARGET_CASES:
        pairs = rng.randint(0, 140)
        single = rng.randint(-10**6, 10**6)
        nums = []
        used = {single}
        for _ in range(pairs):
            value = rng.randint(-10**6, 10**6)
            while value in used:
                value = rng.randint(-10**6, 10**6)
            used.add(value)
            nums.extend([value, value])
        nums.append(single)
        nums.sort()
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
                description="You are given a sorted array consisting of only integers where every element appears exactly twice, except for one element which appears exactly once.\n\nReturn the single element that appears only once.\n\nYour solution must run in O(log n) time and O(1) space.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums",
                output_format="Single integer: the non-duplicated value",
                constraints="1 <= nums.length <= 10^5\n0 <= nums.length % 2 == 1\n-10^9 <= nums[i] <= 10^9",
                method_name="singleNonDuplicate",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1250,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
