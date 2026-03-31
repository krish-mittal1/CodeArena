import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Search in Rotated Sorted Array"


def solve(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def rotate(arr: list[int], k: int) -> list[int]:
    if not arr:
        return arr
    k %= len(arr)
    return arr[k:] + arr[:k]


def make_case(nums: list[int], target: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(nums) + "\n" + json.dumps(target),
        "expected_output": json.dumps(solve(nums, target)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, target in [([4, 5, 6, 7, 0, 1, 2], 0), ([4, 5, 6, 7, 0, 1, 2], 3)]:
        cases.append(make_case(nums, target, idx, True))
        idx += 1

    fixed = [
        ([1], 1), ([1], 0), ([3, 1], 1), ([3, 1], 3), ([5, 1, 3], 3),
        ([6, 7, 1, 2, 3, 4, 5], 4), ([1, 2, 3, 4, 5], 4), ([1, 2, 3, 4, 5], 0),
    ]
    for nums, target in fixed:
        cases.append(make_case(nums, target, idx))
        idx += 1

    for n in [5, 10, 20, 50, 100]:
        base = list(range(n))
        for rot in range(n):
            nums = rotate(base, rot)
            cases.append(make_case(nums, nums[0], idx)); idx += 1
            cases.append(make_case(nums, nums[-1], idx)); idx += 1
            cases.append(make_case(nums, n + 7, idx)); idx += 1
            if len(cases) >= 170:
                break
        if len(cases) >= 170:
            break

    rng = random.Random(20260331)
    while len(cases) < 210:
        n = rng.randint(1, 200)
        base = sorted(set(rng.randint(-500, 500) for _ in range(n)))
        if not base:
            base = [0]
        nums = rotate(base, rng.randint(0, len(base) - 1))
        target = nums[rng.randint(0, len(nums) - 1)] if rng.randint(0, 1) else rng.randint(-600, 600)
        cases.append(make_case(nums, target, idx))
        idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        description = (
            "Given a sorted array of distinct integers that has been rotated at an unknown pivot, return the "
            "index of target if it exists, otherwise return -1.\n\n"
            "Example 1\nInput: nums = [4,5,6,7,0,1,2], target = 0\nOutput: 4\n\n"
            "Example 2\nInput: nums = [4,5,6,7,0,1,2], target = 3\nOutput: -1"
        )
        kwargs = dict(
            description=description,
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array nums (int[])\nLine 2: integer target",
            output_format="Single integer: index of target or -1",
            constraints="1 <= nums.length <= 5000\nAll nums are distinct",
            method_name="search",
            parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1100,
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
