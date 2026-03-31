import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Reverse Linked List"


def solve(values: list[int]) -> list[int]:
    return list(reversed(values))


def make_case(values: list[int], idx: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(values),
        "expected_output": json.dumps(solve(values)),
        "order_index": idx,
        "is_sample": is_sample,
    }


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for values in [[1, 2, 3, 4, 5], [1, 2], []]:
        cases.append(make_case(values, idx, True)); idx += 1
    fixed = [[1], [0], [-1], [5, 5, 5], [-3, -2, -1], [10**9, -10**9, 0]]
    for values in fixed:
        cases.append(make_case(values, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(0, 300)
        values = [rng.randint(-10**4, 10**4) for _ in range(n)]
        cases.append(make_case(values, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given the head of a singly linked list, reverse the list and return the new head.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array of node values. The runner converts this array into head: ListNode.",
            output_format="JSON array representing the reversed linked list",
            constraints="0 <= number of nodes <= 5000\n-10^4 <= Node.val <= 10^4",
            method_name="reverseList",
            parameters=[{"name": "head", "type": "ListNode"}],
            return_type="ListNode",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=900,
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
