import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Reverse Linked List II"


def solve(values: list[int], left: int, right: int) -> list[int]:
    if not values:
        return []
    left -= 1
    right -= 1
    return values[:left] + list(reversed(values[left:right + 1])) + values[right + 1:]


def make_case(values: list[int], left: int, right: int, idx: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(values) + "\n" + json.dumps(left) + "\n" + json.dumps(right),
        "expected_output": json.dumps(solve(values, left, right)),
        "order_index": idx,
        "is_sample": is_sample,
    }


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for values, left, right in [([1, 2, 3, 4, 5], 2, 4), ([5], 1, 1)]:
        cases.append(make_case(values, left, right, idx, True)); idx += 1
    fixed = [([1, 2], 1, 2), ([1, 2, 3], 1, 2), ([1, 2, 3], 2, 3), ([7, 7, 7, 7], 2, 3)]
    for values, left, right in fixed:
        cases.append(make_case(values, left, right, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        length = rng.randint(1, 220)
        values = [rng.randint(-5000, 5000) for _ in range(length)]
        left = rng.randint(1, length)
        right = rng.randint(left, length)
        cases.append(make_case(values, left, right, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given the head of a singly linked list and two positions left and right, reverse the nodes of the list from position left to position right and return the modified list.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array of node values\nLine 2: integer left\nLine 3: integer right. The runner converts the array into head: ListNode.",
            output_format="JSON array representing the linked list after the sublist reversal",
            constraints="1 <= number of nodes <= 5000\n1 <= left <= right <= number of nodes",
            method_name="reverseBetween",
            parameters=[{"name": "head", "type": "ListNode"}, {"name": "left", "type": "int"}, {"name": "right", "type": "int"}],
            return_type="ListNode",
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
