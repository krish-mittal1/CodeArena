import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Product of Array Except Self"
TARGET_CASES = 643


def solve(nums: list[int]) -> list[int]:
    n = len(nums)
    answer = [1] * n
    prefix = 1
    for i in range(n):
        answer[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix
        suffix *= nums[i]
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for nums in ([1, 2, 3, 4], [-1, 1, 0, -3, 3], [0, 0]):
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [5],
        [2, 0, 4],
        [0, 1, 2, 3],
        [1, -1, 1, -1],
        [3, 3, 3, 3],
        [-2, -3, -4],
        [10, 0, 0, 5],
        [1000, -1000, 1, -1],
    ]
    for nums in fixed:
        cases.append(make_case(nums, expected_output=solve(nums), idx=idx))
        idx += 1

    rng = random.Random(2026040207)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 200)
        nums = [rng.randint(-6, 6) for _ in range(n)]
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
                description="Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].\n\nThe product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums",
                output_format="JSON array answer",
                constraints="1 <= nums.length <= 200\n-6 <= nums[i] <= 6\nThe product of any prefix or suffix fits in 32-bit signed integer.",
                method_name="productExceptSelf",
                parameters=[{"name": "nums", "type": "int[]"}],
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
