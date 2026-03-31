import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Merge Two Sorted Lists"


def solve(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def make_case(a: list[int], b: list[int], idx: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(a) + "\n" + json.dumps(b),
        "expected_output": json.dumps(solve(a, b)),
        "order_index": idx,
        "is_sample": is_sample,
    }


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for a, b in [([1, 2, 4], [1, 3, 4]), ([], []), ([], [0])]:
        cases.append(make_case(a, b, idx, True)); idx += 1
    fixed = [([1], []), ([], [1]), ([1, 1, 2], [1, 3]), ([-5, -3], [-4, -2, -1]), ([0, 0], [0])]
    for a, b in fixed:
        cases.append(make_case(a, b, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n1 = rng.randint(0, 120); n2 = rng.randint(0, 120)
        a = sorted(rng.randint(-2000, 2000) for _ in range(n1))
        b = sorted(rng.randint(-2000, 2000) for _ in range(n2))
        cases.append(make_case(a, b, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="You are given the heads of two sorted linked lists. Merge them into one sorted linked list and return its head.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array list1\nLine 2: JSON array list2. The runner converts each array into a ListNode chain.",
            output_format="JSON array representing the merged sorted linked list",
            constraints="0 <= nodes in both lists <= 5000\n-10^4 <= Node.val <= 10^4",
            method_name="mergeTwoLists",
            parameters=[{"name": "list1", "type": "ListNode"}, {"name": "list2", "type": "ListNode"}],
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
