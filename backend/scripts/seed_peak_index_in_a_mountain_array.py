import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Peak Index in a Mountain Array"
TARGET_CASES = 517


def solve(arr: list[int]) -> int:
    left, right = 1, len(arr) - 2
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < arr[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left


def build_mountain(up_len: int, down_len: int, start: int, step: int) -> list[int]:
    peak = start + step * up_len
    up = [start + step * i for i in range(up_len)]
    down = [peak - step * i for i in range(down_len + 1)]
    return up + down


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [[0, 1, 0], [0, 2, 1, 0], [3, 5, 3, 2, 0]]
    for arr in samples:
        cases.append(make_case(arr, expected_output=solve(arr), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1, 3, 2],
        [1, 2, 3, 2, 1],
        [1, 5, 9, 12, 7, 4, 2],
        [0, 10, 5, 2],
        [2, 4, 6, 8, 10, 7, 3],
        [5, 6, 7, 8, 9, 4],
        [10, 20, 15],
        [1, 4, 7, 11, 15, 12, 9, 2],
    ]
    for arr in fixed:
        cases.append(make_case(arr, expected_output=solve(arr), idx=idx))
        idx += 1

    rng = random.Random(2026040206)
    while len(cases) < TARGET_CASES:
        up_len = rng.randint(1, 120)
        down_len = rng.randint(1, 120)
        arr = build_mountain(up_len, down_len, rng.randint(-1000, 1000), rng.randint(1, 8))
        cases.append(make_case(arr, expected_output=solve(arr), idx=idx))
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
                description="You are given an integer mountain array arr where arr.length >= 3.\n\nReturn the index i such that arr[0] < ... < arr[i - 1] < arr[i] > arr[i + 1] > ... > arr[arr.length - 1].\n\nYou must solve it in O(log n) time.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array arr",
                output_format="Single integer: the peak index",
                constraints="3 <= arr.length <= 10^5\n0 <= arr[i] <= 10^9\narr is guaranteed to be a mountain array.",
                method_name="peakIndexInMountainArray",
                parameters=[{"name": "arr", "type": "int[]"}],
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
