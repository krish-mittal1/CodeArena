import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Merge Sorted Array"
TARGET_CASES = 512


def solve(nums1: list[int], m: int, nums2: list[int], n: int) -> list[int]:
    merged = nums1[:m] + nums2[:n]
    merged.sort()
    return merged


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3),
        ([1], 1, [], 0),
        ([0], 0, [1], 1),
    ]
    for nums1, m, nums2, n in samples:
        cases.append(make_case(nums1, m, nums2, n, expected_output=solve(nums1, m, nums2, n), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([2, 0], 1, [1], 1),
        ([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3),
        ([0, 0, 0], 0, [2, 5, 6], 3),
        ([-3, -2, -1, 0, 0], 3, [-5, -4], 2),
        ([1, 2, 4, 5, 6, 0], 5, [3], 1),
        ([10, 20, 30, 0, 0, 0], 3, [1, 2, 40], 3),
        ([1, 0], 1, [2], 1),
        ([2, 0], 1, [2], 1),
    ]
    for nums1, m, nums2, n in fixed:
        cases.append(make_case(nums1, m, nums2, n, expected_output=solve(nums1, m, nums2, n), idx=idx))
        idx += 1

    rng = random.Random(2026040204)
    while len(cases) < TARGET_CASES:
        m = rng.randint(0, 180)
        n = rng.randint(0, 180)
        if m == 0 and n == 0:
            n = 1
        left = sorted(rng.randint(-10**4, 10**4) for _ in range(m))
        right = sorted(rng.randint(-10**4, 10**4) for _ in range(n))
        nums1 = left + [0] * n
        cases.append(make_case(nums1, m, right, n, expected_output=solve(nums1, m, right, n), idx=idx))
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
                description="You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of valid elements in nums1 and nums2 respectively.\n\nMerge nums1 and nums2 into a single array sorted in non-decreasing order.\n\nOn this platform, return the final merged nums1 array.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: JSON array nums1\nLine 2: integer m\nLine 3: JSON array nums2\nLine 4: integer n",
                output_format="JSON array representing the merged sorted array",
                constraints="0 <= m, n <= 180\n1 <= m + n <= 360\n-10^4 <= nums1[i], nums2[i] <= 10^4",
                method_name="merge",
                parameters=[
                    {"name": "nums1", "type": "int[]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "int[]"},
                    {"name": "n", "type": "int"},
                ],
                return_type="int[]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=950,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
