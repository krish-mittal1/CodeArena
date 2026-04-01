import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Maximum Subarray"
TARGET_CASES = 587


def solve(nums: list[int]) -> int:
    best = nums[0]
    current = nums[0]
    for value in nums[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for nums in ([-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8]):
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [-1],
        [-5, -2, -9],
        [0, 0, 0],
        [1, 2, 3, 4],
        [-2, -1],
        [8, -19, 5, -4, 20],
        [100, -1, -2, -3, 50],
        [-10, 4, -1, 2, 1, -5, 4],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040203)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 420)
        nums = [rng.randint(-10**4, 10**4) for _ in range(n)]
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
                description="Given an integer array nums, find the subarray with the largest sum, and return its sum.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums",
                output_format="Single integer: maximum subarray sum",
                constraints="1 <= nums.length <= 420\n-10^4 <= nums[i] <= 10^4",
                method_name="maxSubArray",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1100,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
