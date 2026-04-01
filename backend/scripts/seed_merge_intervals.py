import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Merge Intervals"
TARGET_CASES = 682


def solve(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    ordered = sorted((interval[:] for interval in intervals), key=lambda item: item[0])
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for intervals in (
        [[1, 3], [2, 6], [8, 10], [15, 18]],
        [[1, 4], [4, 5]],
        [[1, 4], [0, 4]],
    ):
        cases.append(make_case(intervals, expected_output=solve(intervals), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [[1, 2]],
        [[1, 4], [5, 6]],
        [[5, 7], [1, 3], [2, 4]],
        [[1, 10], [2, 3], [4, 8]],
        [[-10, -1], [-5, 0], [1, 2]],
        [[1, 5], [2, 3], [4, 6], [7, 8]],
        [[0, 0], [0, 1], [2, 2]],
        [[1, 100], [20, 30], [31, 40], [90, 120]],
    ]
    for intervals in fixed:
        cases.append(make_case(intervals, expected_output=solve(intervals), idx=idx))
        idx += 1

    rng = random.Random(2026040210)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 180)
        intervals: list[list[int]] = []
        base = rng.randint(-200, 200)
        for _ in range(n):
            start = base + rng.randint(-50, 120)
            end = start + rng.randint(0, 50)
            intervals.append([start, end])
        cases.append(make_case(intervals, expected_output=solve(intervals), idx=idx))
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
                description="Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals and return an array of the non-overlapping intervals that cover all the intervals in the input.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON 2D array intervals",
                output_format="JSON 2D array of merged intervals",
                constraints="1 <= intervals.length <= 180\nintervals[i].length == 2\n-10^4 <= starti <= endi <= 10^4",
                method_name="merge",
                parameters=[{"name": "intervals", "type": "int[][]"}],
                return_type="int[][]",
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
