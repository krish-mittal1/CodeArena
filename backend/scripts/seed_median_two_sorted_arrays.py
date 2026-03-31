import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Median of Two Sorted Arrays"


def median(nums1: list[int], nums2: list[int]):
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2:
        return merged[n // 2]
    return (merged[n // 2 - 1] + merged[n // 2]) / 2


def make_case(nums1: list[int], nums2: list[int], order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums1) + "\n" + json.dumps(nums2),
        "expected_output": json.dumps(median(nums1, nums2)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums1, nums2 in [([1, 3], [2]), ([1, 2], [3, 4])]:
        cases.append(make_case(nums1, nums2, idx, True))
        idx += 1
    for nums1, nums2 in [([], [1]), ([2], []), ([0, 0], [0, 0]), ([-5, -3], [-2, -1]), ([1], [2, 3, 4, 5])]:
        cases.append(make_case(nums1, nums2, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 170:
        n1 = rng.randint(0, 60)
        n2 = rng.randint(1 if n1 == 0 else 0, 60)
        nums1 = sorted(rng.randint(-1000, 1000) for _ in range(n1))
        nums2 = sorted(rng.randint(-1000, 1000) for _ in range(n2))
        cases.append(make_case(nums1, nums2, idx))
        idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given two sorted arrays nums1 and nums2, return the median of the combined numbers.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array nums1 (int[])\nLine 2: JSON array nums2 (int[])",
            output_format="Single number: median value",
            constraints="1 <= nums1.length + nums2.length <= 2000",
            method_name="findMedianSortedArrays",
            parameters=[{"name": "nums1", "type": "int[]"}, {"name": "nums2", "type": "int[]"}],
            return_type="float",
            time_limit_ms=2500,
            memory_limit_mb=256,
            rating=1500,
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
