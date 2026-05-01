import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import random
import json
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import AsyncSessionLocal
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.core.constants import Difficulty

async def main():
    async with AsyncSessionLocal() as db:
        # Create the Problem
        problem = Problem(
            title="Find Minimum in Rotated Sorted Array",
            description='''Given an integer array nums of size N, sorted in ascending order with distinct values, and then rotated an unknown number of times (between 1 and N), find the minimum element in the array.

**Example 1**

Input: `nums = [4, 5, 6, 7, 0, 1, 2, 3]`

Output: `0`

Explanation: Here, the element 0 is the minimum element in the array.

**Example 2**

Input: `nums = [3, 4, 5, 1, 2]`

Output: `1`

Explanation: Here, the element 1 is the minimum element in the array.

**Example 3**

Input: `nums = [4, 5, 6, 7, -7, 1, 2, 3]`

Output: `-7`''',
            difficulty=Difficulty.EASY.value,
            input_format="An integer array `nums` of unique elements.",
            output_format="An integer representing the minimum element.",
            constraints="""- `n == nums.length`
- `1 <= n <= 10^4`
- `-10^4 <= nums[i] <= 10^4`
- All the integers of `nums` are unique.
- `nums` is sorted and rotated between `1` and `n` times.""",
            method_name="findMin",
            parameters=[{"name": "nums", "type": "int[]"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=850, # 850 makes it Easy matchmaking band
            is_active=True
        )
        db.add(problem)
        await db.flush()

        test_cases = []
        
        # Add sample cases specified by user
        samples = [
            {"nums": [4, 5, 6, 7, 0, 1, 2, 3], "ans": 0},
            {"nums": [3, 4, 5, 1, 2], "ans": 1},
            {"nums": [4, 5, 6, 7, -7, 1, 2, 3], "ans": -7}
        ]
        
        order_idx = 0
        for s in samples:
            tc = TestCase(
                problem_id=problem.id,
                input=s["nums"] if isinstance(s["nums"], str) else str(s["nums"]), # Note: backend executor might expect raw string or json. Usually Leetcode style executor parser stringified inputs. we use json dumps to be safe
                expected_output=str(s["ans"]),
                is_sample=True,
                order_index=order_idx
            )
            tc.input = json.dumps(s["nums"])
            test_cases.append(tc)
            order_idx += 1

        # Generate ~150 random/edge test cases
        
        # Edge case: size 1
        tc_edge_1 = TestCase(problem_id=problem.id, input="[42]", expected_output="42", is_sample=False, order_index=order_idx)
        test_cases.append(tc_edge_1)
        order_idx += 1
        
        # Edge case: size 2
        tc_edge_2 = TestCase(problem_id=problem.id, input="[2, 1]", expected_output="1", is_sample=False, order_index=order_idx)
        test_cases.append(tc_edge_2)
        order_idx += 1
        
        # Generate random cases
        for _ in range(150):
            n = random.randint(1, 1000) # using smaller n for sanity, up to 1000 instead of 10000 to keep DB quick
            start_val = random.randint(-9000, 9000)
            arr = list(range(start_val, start_val + n))
            # it asserts unique values
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
        print(f"Added Problem: {problem.title} with {len(test_cases)} test cases.")

if __name__ == "__main__":
    asyncio.run(main())
