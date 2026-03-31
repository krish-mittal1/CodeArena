import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Gas Station"


def solve(gas: list[int], cost: list[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    total = 0
    start = 0
    for i, (g, c) in enumerate(zip(gas, cost)):
        total += g - c
        if total < 0:
            total = 0
            start = i + 1
    return start


def make_case(gas: list[int], cost: list[int], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(gas) + "\n" + json.dumps(cost), "expected_output": json.dumps(solve(gas, cost)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for gas, cost in [([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3])]:
        cases.append(make_case(gas, cost, idx, True)); idx += 1
    fixed = [([5], [4]), ([2], [3]), ([3, 1, 1], [1, 2, 2]), ([2, 2, 2], [2, 2, 2]), ([6, 1, 4, 3, 5], [3, 8, 2, 4, 2])]
    for gas, cost in fixed:
        cases.append(make_case(gas, cost, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(1, 180)
        gas = [rng.randint(0, 9) for _ in range(n)]
        cost = [rng.randint(0, 9) for _ in range(n)]
        cases.append(make_case(gas, cost, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="There are n gas stations on a circular route. gas[i] is the fuel at station i and cost[i] is the fuel needed to go from i to i+1. Return the starting station index if you can complete the circuit once, otherwise return -1.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array gas (int[])\nLine 2: JSON array cost (int[])",
            output_format="Single integer: starting index or -1",
            constraints="1 <= gas.length == cost.length <= 10^5\n0 <= gas[i], cost[i] <= 10^4",
            method_name="canCompleteCircuit",
            parameters=[{"name": "gas", "type": "int[]"}, {"name": "cost", "type": "int[]"}],
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
