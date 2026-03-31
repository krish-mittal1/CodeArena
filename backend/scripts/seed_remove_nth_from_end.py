import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Remove Nth Node From End of List"


def solve(values: list[int], n: int) -> list[int]:
    if not values:
        return []
    idx = len(values) - n
    if 0 <= idx < len(values):
        return values[:idx] + values[idx + 1 :]
    return values


def make_case(values: list[int], n: int, idx: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(values) + "\n" + json.dumps(n),
        "expected_output": json.dumps(solve(values, n)),
        "order_index": idx,
        "is_sample": is_sample,
    }


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for values, n in [([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 1)]:
        cases.append(make_case(values, n, idx, True)); idx += 1
    fixed = [([1, 2], 2), ([5, 5, 5], 2), ([-3, -2, -1, 0], 4), ([1, 3, 5, 7, 9], 5)]
    for values, n in fixed:
        cases.append(make_case(values, n, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        length = rng.randint(1, 220)
        values = [rng.randint(-5000, 5000) for _ in range(length)]
        n = rng.randint(1, length)
        cases.append(make_case(values, n, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given the head of a linked list, remove its nth node from the end and return the head of the modified list.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array of node values\nLine 2: integer n. The runner converts the array into head: ListNode.",
            output_format="JSON array representing the linked list after removal",
            constraints="1 <= number of nodes <= 5000\n1 <= n <= number of nodes",
            method_name="removeNthFromEnd",
            parameters=[{"name": "head", "type": "ListNode"}, {"name": "n", "type": "int"}],
            return_type="ListNode",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1100,
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
