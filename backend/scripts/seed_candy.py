import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Candy"


def solve(ratings: list[int]) -> int:
    n = len(ratings)
    if n == 0:
        return 0
    candy = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candy[i] = candy[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candy[i] = max(candy[i], candy[i + 1] + 1)
    return sum(candy)


def make_case(ratings: list[int], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(ratings), "expected_output": json.dumps(solve(ratings)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for ratings in [[1, 0, 2], [1, 2, 2]]:
        cases.append(make_case(ratings, idx, True)); idx += 1
    for ratings in [[], [5], [1, 1, 1], [1, 3, 4, 5, 2], [1, 2, 3, 1, 0], [5, 4, 3, 2, 1]]:
        cases.append(make_case(ratings, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(0, 200)
        ratings = [rng.randint(0, 20) for _ in range(n)]
        cases.append(make_case(ratings, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="There are children standing in a line with ratings. Give each child at least one candy, and children with a higher rating than an adjacent child must get more candies. Return the minimum candies needed.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array ratings (int[])",
            output_format="Single integer: minimum candies",
            constraints="1 <= ratings.length <= 2 * 10^4",
            method_name="candy",
            parameters=[{"name": "ratings", "type": "int[]"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1300,
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
