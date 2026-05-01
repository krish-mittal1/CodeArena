import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import random
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.session import AsyncSessionLocal
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.core.constants import Difficulty

TITLE = "Find Minimum in Rotated Sorted Array"

DESCRIPTION = """Given an integer array nums of size N, sorted in ascending order with distinct values, and then rotated an unknown number of times (between 1 and N), find the minimum element in the array.

Example 1
Input : nums = [4, 5, 6, 7, 0, 1, 2, 3]
Output: 0
Explanation: Here, the element 0 is the minimum element in the array.

Example 2
Input : nums = [3, 4, 5, 1, 2]
Output: 1
Explanation: Here, the element 1 is the minimum element in the array.

Example 3
Input : nums = [4, 5, 6, 7, -7, 1, 2, 3]
Output: -7"""

CONSTRAINTS = """n == nums.length
1 <= n <= 10^4
-10^4 <= nums[i] <= 10^4
All the integers of nums are unique.
nums is sorted and rotated between 1 and n times."""

INPUT_FORMAT = "An integer array nums of unique elements."
OUTPUT_FORMAT = "An integer representing the minimum element."


async def main():
    async with AsyncSessionLocal() as db:
        # Check if problem already exists — update it instead of duplicating
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        if problem:
            # UPDATE existing problem's text fields
            problem.description = DESCRIPTION
            problem.constraints = CONSTRAINTS
            problem.input_format = INPUT_FORMAT
            problem.output_format = OUTPUT_FORMAT
            await db.commit()
            print(f"Updated existing problem: {TITLE}")
            return

        # CREATE new problem + test cases
        problem = Problem(
            title=TITLE,
            description=DESCRIPTION,
            difficulty=Difficulty.EASY.value,
            input_format=INPUT_FORMAT,
            output_format=OUTPUT_FORMAT,
            constraints=CONSTRAINTS,
            method_name="findMin",
            parameters=[{"name": "nums", "type": "int[]"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=850,
            is_active=True
        )
        db.add(problem)
        await db.flush()

        test_cases = []

        # Sample cases
        samples = [
            {"nums": [4, 5, 6, 7, 0, 1, 2, 3], "ans": 0},
            {"nums": [3, 4, 5, 1, 2], "ans": 1},
            {"nums": [4, 5, 6, 7, -7, 1, 2, 3], "ans": -7}
        ]

        order_idx = 0
        for s in samples:
            tc = TestCase(
                problem_id=problem.id,
                input=json.dumps(s["nums"]),
                expected_output=str(s["ans"]),
                is_sample=True,
                order_index=order_idx
            )
            test_cases.append(tc)
            order_idx += 1

        # Edge cases
        test_cases.append(TestCase(problem_id=problem.id, input="[42]", expected_output="42", is_sample=False, order_index=order_idx))
        order_idx += 1
        test_cases.append(TestCase(problem_id=problem.id, input="[2, 1]", expected_output="1", is_sample=False, order_index=order_idx))
        order_idx += 1

        # Generate 150 random cases
        for _ in range(150):
            n = random.randint(1, 1000)
            start_val = random.randint(-9000, 9000)
            arr = list(range(start_val, start_val + n))
            k = random.randint(1, n)
            rotated = arr[-k:] + arr[:-k]
            ans = min(rotated)

            tc = TestCase(
                problem_id=problem.id,
                input=json.dumps(rotated),
                expected_output=str(ans),
                is_sample=False,
                order_index=order_idx
            )
            test_cases.append(tc)
            order_idx += 1

        db.add_all(test_cases)
        await db.commit()
        print(f"Added Problem: {TITLE} with {len(test_cases)} test cases.")


if __name__ == "__main__":
    asyncio.run(main())
