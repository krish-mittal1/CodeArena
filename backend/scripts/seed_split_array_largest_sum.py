import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Split Array Largest Sum"
TARGET_CASES = 584


def solve(nums: list[int], k: int) -> int:
    left, right = max(nums), sum(nums)
    answer = right
    while left <= right:
        mid = (left + right) // 2
        pieces = 1
        current = 0
        for value in nums:
            if current + value > mid:
                pieces += 1
                current = 0
            current += value
        if pieces <= k:
            answer = mid
            right = mid - 1
        else:
            left = mid + 1
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([7, 2, 5, 10, 8], 2),
        ([1, 2, 3, 4, 5], 2),
        ([1, 4, 4], 3),
    ]
    for nums, k in samples:
        cases.append(make_case(nums, k, expected_output=solve(nums, k), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([5], 1),
        ([5, 5, 5, 5], 1),
        ([5, 5, 5, 5], 4),
        ([1, 100, 1, 100, 1], 3),
        ([9, 8, 7, 6, 5], 5),
        ([9, 8, 7, 6, 5], 2),
        ([1, 2, 3, 4, 5, 6], 6),
        ([10, 1, 1, 1, 10], 2),
    ]
    for nums, k in fixed:
        cases.append(make_case(nums, k, expected_output=solve(nums, k), idx=idx))
        idx += 1

    rng = random.Random(2026040212)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 220)
        nums = [rng.randint(1, 1000) for _ in range(n)]
        k = rng.randint(1, n)
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
                description="Given an integer array nums and an integer k, split nums into k non-empty contiguous subarrays.\n\nWrite an algorithm to minimize the largest sum among these subarrays.\n\nReturn the minimized largest sum.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: JSON array nums\nLine 2: integer k",
                output_format="Single integer: minimized largest sum",
                constraints="1 <= nums.length <= 1000\n0 <= nums[i] <= 10^6\n1 <= k <= min(50, nums.length)",
                method_name="splitArray",
                parameters=[{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
                return_type="int",
                time_limit_ms=2500,
                memory_limit_mb=256,
                rating=1550,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
