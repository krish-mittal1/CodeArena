import asyncio
import json
import random
from bisect import bisect_left

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Search Insert Position"


def make_case(nums: list[int], target: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(target),
        "expected_output": json.dumps(bisect_left(nums, target)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, target in [([1, 3, 5, 6], 5), ([1, 3, 5, 6], 2)]:
        cases.append(make_case(nums, target, idx, True))
        idx += 1
    for nums, target in [([], 1), ([1], 0), ([1], 1), ([1], 2), ([1, 3], 2), ([1, 3], 4)]:
        cases.append(make_case(nums, target, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(0, 250)
        nums = sorted(set(rng.randint(-700, 700) for _ in range(n)))
        target = rng.randint(-800, 800)
        cases.append(make_case(nums, target, idx))
        idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description=(
                "Given a sorted array of distinct integers and a target value, return the index if the target "
                "exists. Otherwise return the index where it should be inserted to keep the array sorted."
            ),
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array nums (int[])\nLine 2: integer target",
            output_format="Single integer: insertion index",
            constraints="0 <= nums.length <= 10^4\nnums is strictly increasing",
            method_name="searchInsert",
            parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=800,
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
