import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Jump Game II"


def solve(nums: list[int]) -> int:
    if len(nums) <= 1:
        return 0
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps


def make_case(nums: list[int], idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(nums), "expected_output": json.dumps(solve(nums)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for nums in [[2, 3, 1, 1, 4], [2, 3, 0, 1, 4]]:
        cases.append(make_case(nums, idx, True)); idx += 1
    fixed = [[0], [1], [1, 1], [2, 1], [1, 2, 1, 1, 1], [5, 0, 0, 0, 0], [3, 4, 2, 1, 0, 4, 2, 0]]
    for nums in fixed:
        cases.append(make_case(nums, idx)); idx += 1
    rng = random.Random(20260331)
    while len(cases) < 180:
        n = rng.randint(1, 250)
        nums = [rng.randint(1, 8) for _ in range(n)]
        nums[-1] = 0
        cases.append(make_case(nums, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given an array nums where each element is your maximum jump length from that position, return the minimum number of jumps needed to reach the last index.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array nums (int[])",
            output_format="Single integer: minimum number of jumps",
            constraints="1 <= nums.length <= 10^4\n0 <= nums[i] <= 10^5\nThe last index is reachable",
            method_name="jump",
            parameters=[{"name": "nums", "type": "int[]"}],
            return_type="int",
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
