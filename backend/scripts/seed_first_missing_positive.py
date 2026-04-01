import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "First Missing Positive"
TARGET_CASES = 761


def solve(nums: list[int]) -> int:
    seen = {value for value in nums if value > 0}
    candidate = 1
    while candidate in seen:
        candidate += 1
    return candidate


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for nums in ([1, 2, 0], [3, 4, -1, 1], [7, 8, 9, 11, 12]):
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [2],
        [1, 1],
        [2, 2, 2],
        [-1, -2, -3],
        [0, 0, 0],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040213)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 280)
        nums = [rng.randint(-100, 300) for _ in range(n)]
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
                description="Given an unsorted integer array nums, return the smallest missing positive integer.\n\nYou must implement an algorithm that runs in O(n) time and uses O(1) auxiliary space in the classic version of the problem.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: JSON array nums",
                output_format="Single integer: first missing positive",
                constraints="1 <= nums.length <= 280\n-2^31 <= nums[i] <= 2^31 - 1",
                method_name="firstMissingPositive",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1500,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
