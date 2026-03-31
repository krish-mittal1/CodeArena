import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Palindrome Linked List"


def solve(values: list[int]) -> bool:
    return values == values[::-1]


def make_case(values: list[int], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(values), "expected_output": json.dumps(solve(values)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for values in [[1, 2, 2, 1], [1, 2]]:
        cases.append(make_case(values, idx, True)); idx += 1
    for values in [[], [1], [1, 1], [1, 2, 1], [1, 2, 3, 2, 1], [1, 2, 3, 4], [7, 7, 7]]:
        cases.append(make_case(values, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(0, 220)
        values = [rng.randint(-1000, 1000) for _ in range(n)]
        cases.append(make_case(values, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given the head of a singly linked list, return true if it is a palindrome, otherwise return false.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array of node values. The runner converts it into head: ListNode.",
            output_format="Boolean: true if the linked list is a palindrome",
            constraints="0 <= number of nodes <= 10^5",
            method_name="isPalindrome",
            parameters=[{"name": "head", "type": "ListNode"}],
            return_type="bool",
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
