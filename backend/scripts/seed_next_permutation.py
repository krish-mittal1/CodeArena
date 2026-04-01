import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Next Permutation"
TARGET_CASES = 733


def solve(nums: list[int]) -> list[int]:
    arr = nums[:]
    pivot = len(arr) - 2
    while pivot >= 0 and arr[pivot] >= arr[pivot + 1]:
        pivot -= 1
    if pivot >= 0:
        swap = len(arr) - 1
        while arr[swap] <= arr[pivot]:
            swap -= 1
        arr[pivot], arr[swap] = arr[swap], arr[pivot]
    left = pivot + 1
    right = len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    return arr


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for nums in ([1, 2, 3], [3, 2, 1], [1, 1, 5]):
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [1, 3, 2],
        [2, 2, 0, 1],
        [1, 5, 1],
        [2, 3, 1],
        [1, 2, 2, 3],
        [5, 4, 7, 5, 3, 2],
        [2, 2, 7, 5, 4, 3, 2, 2, 1],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040211)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 8)
        nums = [rng.randint(0, 7) for _ in range(n)]
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
                description="A permutation of an array of integers is an arrangement of its members into a sequence or linear order.\n\nGiven an array nums, find the next permutation of nums.\n\nOn this platform, return the modified array after computing the next lexicographically greater permutation. If such an arrangement is not possible, return the lowest possible order.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: JSON array nums",
                output_format="JSON array representing the next permutation",
                constraints="1 <= nums.length <= 8\n0 <= nums[i] <= 100",
                method_name="nextPermutation",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int[]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1450,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
