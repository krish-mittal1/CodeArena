import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Middle of the Linked List"


def solve(values: list[int]) -> list[int]:
    return values[len(values) // 2 :]


def make_case(values: list[int], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(values), "expected_output": json.dumps(solve(values)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for values in [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6]]:
        cases.append(make_case(values, idx, True)); idx += 1
    for values in [[1], [1, 2], [7, 7, 7], [-5, -4, -3, -2], [0, 1, 0, 1, 0]]:
        cases.append(make_case(values, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 170:
        n = rng.randint(1, 250)
        values = [rng.randint(-5000, 5000) for _ in range(n)]
        cases.append(make_case(values, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given the head of a singly linked list, return the middle node. If there are two middle nodes, return the second one.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array of node values. The runner converts it into head: ListNode.",
            output_format="JSON array representing the linked list starting from the returned middle node",
            constraints="1 <= number of nodes <= 10^5",
            method_name="middleNode",
            parameters=[{"name": "head", "type": "ListNode"}],
            return_type="ListNode",
            time_limit_ms=1200,
            memory_limit_mb=256,
            rating=800,
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
