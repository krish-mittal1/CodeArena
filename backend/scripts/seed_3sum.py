"""
Seed script — insert '3 Sum' problem with 100+ test cases.

Usage: python -m backend.scripts.seed_3sum
"""
import asyncio
import logging
import random
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from backend.config import settings
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.core.constants import Difficulty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def solve_3sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums)):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s > 0:
                right -= 1
            elif s < 0:
                left += 1
            else:
                res.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
    return res

def build_test_case(nums, is_sample=False, order_index=0):
    input_str = f"{len(nums)}\n"
    input_str += " ".join(map(str, nums))
    
    expected_list = solve_3sum(nums)
    output_str = f"{len(expected_list)}\n"
    for t in expected_list:
        output_str += " ".join(map(str, t)) + "\n"
        
    return {
        "input": input_str.strip(),
        "expected_output": output_str.strip(),
        "is_sample": is_sample,
        "order_index": order_index
    }

async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # 1. Delete old overlapping problems
        targets = ["3 Sum", "3Sum", "Three Sum", "ThreeSum"]
        result = await db.execute(select(Problem).where(Problem.title.in_(targets)))
        old_probs = list(result.scalars().all())
        for op in old_probs:
            logger.info(f"Removing old problem: {op.title}")
            await db.delete(op)
        await db.commit()

        # 2. Create the new problem
        problem_data = {
            "title": "3 Sum",
            "difficulty": Difficulty.MEDIUM,
            "rating": 1500,
            "description": "Given an integer array `nums`, return all triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\nNotice that the solution set must not contain duplicate triplets.",
            "input_format": "First line integer N (length of array).\nNext line contains N space-separated integers representing the array `nums`.",
            "output_format": "Print the number of triplets K on the first line.\nThen print K lines, each containing 3 space-separated integers representing a triplet.\n\nNote for Strict Matching: Elements within each triplet must be sorted in ascending order. The K lines of triplets themselves must be sorted lexicographically.",
            "constraints": "3 <= N <= 1500\n-10^4 <= nums[i] <= 10^4",
            "time_limit_ms": 3000,
            "memory_limit_mb": 256,
        }
        
        problem = Problem(**problem_data)
        db.add(problem)
        await db.flush()

        logger.info(f"Created Problem: {problem.title} (ID: {problem.id})")

        # 3. Generate 100+ Test Cases
        test_cases_data = []
        idx = 0
        
        # Sample 1
        test_cases_data.append(build_test_case([-1, 0, 1, 2, -1, -4], True, idx))
        idx += 1
        
        # Sample 2
        test_cases_data.append(build_test_case([0, 1, 1], True, idx))
        idx += 1
        
        # Sample 3
        test_cases_data.append(build_test_case([0, 0, 0], True, idx))
        idx += 1
        
        # Edge cases
        test_cases_data.append(build_test_case([0, 0, 0, 0], False, idx))
        idx += 1
        test_cases_data.append(build_test_case([-2, 0, 0, 2, 2], False, idx))
        idx += 1
        
        # All positive / all negative (0 triplets)
        test_cases_data.append(build_test_case([1, 2, 3, 4, 5, 6], False, idx))
        idx += 1
        test_cases_data.append(build_test_case([-1, -2, -3, -4, -5, -6], False, idx))
        idx += 1
        
        # Many duplicates
        test_cases_data.append(build_test_case([-2]*50 + [0]*50 + [2]*50, False, idx))
        idx += 1
        
        # Procedurally generate 100 more random arrays
        for _ in range(100):
            N = random.randint(3, 1000)
            nums = [random.randint(-1000, 1000) for _ in range(N)]
            test_cases_data.append(build_test_case(nums, False, idx))
            idx += 1

        for tc in test_cases_data:
            db.add(TestCase(problem_id=problem.id, **tc))
            
        await db.commit()
        logger.info(f"✅ Successfully seeded {idx} test cases for '3 Sum'.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
