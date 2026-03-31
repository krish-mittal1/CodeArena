import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Non-overlapping Intervals"


def solve(intervals: list[list[int]]) -> int:
    intervals = sorted(intervals, key=lambda x: x[1])
    removed = 0
    prev_end = float("-inf")
    for start, end in intervals:
        if start < prev_end:
            removed += 1
        else:
            prev_end = end
    return removed


def make_case(intervals: list[list[int]], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(intervals), "expected_output": json.dumps(solve(intervals)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for intervals in [[[1, 2], [2, 3], [3, 4], [1, 3]], [[1, 2], [1, 2], [1, 2]]]:
        cases.append(make_case(intervals, idx, True)); idx += 1
    for intervals in [[], [[1, 2]], [[1, 100], [11, 22], [1, 11], [2, 12]], [[0, 2], [1, 3], [2, 4], [3, 5]]]:
        cases.append(make_case(intervals, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(0, 120)
        intervals = []
        for _ in range(n):
            a = rng.randint(-100, 100)
            b = rng.randint(a, a + rng.randint(0, 20))
            intervals.append([a, b])
        cases.append(make_case(intervals, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given a list of intervals, return the minimum number of intervals you must remove to make the rest non-overlapping.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array intervals (int[][])",
            output_format="Single integer: minimum removals",
            constraints="1 <= intervals.length <= 10^5",
            method_name="eraseOverlapIntervals",
            parameters=[{"name": "intervals", "type": "int[][]"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1200,
            is_active=True,
        )
        if problem:
            for k, v in kwargs.items():
                setattr(problem, k, v)
            deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id)); await db.flush(); deleted = True
            except Exception:
                await db.rollback(); await db.refresh(problem)
        else:
            problem = Problem(title=TITLE, **kwargs)
            db.add(problem); await db.flush(); deleted = True
        if deleted:
            for tc in build_cases():
                db.add(TestCase(problem_id=problem.id, **tc))
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
