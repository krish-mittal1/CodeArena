import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Rotate Array"
TARGET_CASES = 571


def solve(nums: list[int], k: int) -> list[int]:
    if not nums:
        return []
    k %= len(nums)
    return nums[-k:] + nums[:-k] if k else nums[:]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([1, 2, 3, 4, 5, 6, 7], 3),
        ([-1, -100, 3, 99], 2),
        ([1], 0),
    ]
    for nums, k in samples:
        cases.append(make_case(nums, k, expected_output=solve(nums, k), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 10),
        ([1, 2], 1),
        ([1, 2], 2),
        ([1, 2], 3),
        ([0, 0, 0], 5),
        ([5, 4, 3, 2, 1], 4),
        ([-3, -2, -1], 1),
        ([100, 200, 300, 400], 0),
    ]
    for nums, k in fixed:
        cases.append(make_case(nums, k, expected_output=solve(nums, k), idx=idx))
        idx += 1

    rng = random.Random(2026040208)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 260)
        nums = [rng.randint(-10**5, 10**5) for _ in range(n)]
        k = rng.randint(0, 10**6)
        cases.append(make_case(nums, k, expected_output=solve(nums, k), idx=idx))
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
                description="Given an integer array nums, rotate the array to the right by k steps.\n\nOn this platform, return the final rotated array.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array nums\nLine 2: integer k",
                output_format="JSON array after rotating",
                constraints="1 <= nums.length <= 260\n-10^5 <= nums[i] <= 10^5\n0 <= k <= 10^6",
                method_name="rotate",
                parameters=[{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
                return_type="int[]",
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
