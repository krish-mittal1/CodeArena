import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Two Sum II - Input Array Is Sorted"


def solve(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left + 1, right + 1]
        if total < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]


def make_case(numbers: list[int], target: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(numbers) + "\n" + json.dumps(target),
        "expected_output": json.dumps(solve(numbers, target)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for numbers, target in [([2, 7, 11, 15], 9), ([2, 3, 4], 6)]:
        cases.append(make_case(numbers, target, idx, True)); idx += 1
    for numbers, target in [([-1, 0], -1), ([1, 2], 3), ([1, 3, 4, 5, 7, 10], 13), ([1, 1, 3, 5], 2)]:
        cases.append(make_case(numbers, target, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(2, 120)
        arr = sorted(rng.randint(-500, 500) for _ in range(n))
        i = rng.randint(0, n - 2)
        j = rng.randint(i + 1, n - 1)
        target = arr[i] + arr[j]
        cases.append(make_case(arr, target, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given a 1-indexed array sorted in non-decreasing order, return the 1-based indices of two values whose sum equals target.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array numbers (int[])\nLine 2: integer target",
            output_format="JSON array of two integers: 1-based indices",
            constraints="2 <= numbers.length <= 3 * 10^4\nExactly one valid answer exists",
            method_name="twoSum",
            parameters=[{"name": "numbers", "type": "int[]"}, {"name": "target", "type": "int"}],
            return_type="int[]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1000,
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
