import asyncio
import json
import random
from math import ceil

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Koko Eating Bananas"


def solve(piles: list[int], h: int) -> int:
    left, right = 1, max(piles)
    ans = right
    while left <= right:
        mid = (left + right) // 2
        hours = sum(ceil(p / mid) for p in piles)
        if hours <= h:
            ans = mid
            right = mid - 1
        else:
            left = mid + 1
    return ans


def make_case(piles: list[int], h: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(piles) + "\n" + json.dumps(h),
        "expected_output": json.dumps(solve(piles, h)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for piles, h in [([3, 6, 7, 11], 8), ([30, 11, 23, 4, 20], 5)]:
        cases.append(make_case(piles, h, idx, True))
        idx += 1
    for piles, h in [([1], 1), ([1], 5), ([10], 1), ([100, 1], 2), ([100, 1], 101)]:
        cases.append(make_case(piles, h, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(1, 120)
        piles = [rng.randint(1, 10**5) for _ in range(n)]
        h = rng.randint(n, n * 10)
        cases.append(make_case(piles, h, idx))
        idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Koko must finish all banana piles within h hours. Each hour she picks one pile and eats at most k bananas. Return the minimum integer k that lets her finish on time.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array piles (int[])\nLine 2: integer h",
            output_format="Single integer: minimum eating speed",
            constraints="1 <= piles.length <= 10^4\n1 <= piles[i] <= 10^9\npiles.length <= h",
            method_name="minEatingSpeed",
            parameters=[{"name": "piles", "type": "int[]"}, {"name": "h", "type": "int"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1200,
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
