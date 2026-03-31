import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Container With Most Water"


def solve(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        best = max(best, min(height[left], height[right]) * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


def make_case(height: list[int], order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(height),
        "expected_output": json.dumps(solve(height)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for height in [[1, 8, 6, 2, 5, 4, 8, 3, 7], [1, 1]]:
        cases.append(make_case(height, idx, True)); idx += 1
    for height in [[1, 2], [2, 1], [4, 3, 2, 1, 4], [1, 2, 1], [9, 8, 7, 6, 5]]:
        cases.append(make_case(height, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(2, 300)
        height = [rng.randint(0, 10**4) for _ in range(n)]
        cases.append(make_case(height, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given an array height, choose two lines that together with the x-axis form a container that stores the most water.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array height (int[])",
            output_format="Single integer: maximum area",
            constraints="2 <= height.length <= 10^5",
            method_name="maxArea",
            parameters=[{"name": "height", "type": "int[]"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1100,
            is_active=True,
        )
        if problem:
            for k, v in kwargs.items():
                setattr(problem, k, v)
            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception:
                await db.rollback()
                await db.refresh(problem)
        else:
            problem = Problem(title=TITLE, **kwargs)
            db.add(problem)
            await db.flush()
            test_cases_deleted = True
        if test_cases_deleted:
            for tc in build_test_cases():
                db.add(TestCase(problem_id=problem.id, **tc))
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
