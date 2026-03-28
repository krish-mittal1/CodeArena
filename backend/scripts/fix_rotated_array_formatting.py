"""One-time script to fix the description and constraints formatting for
'Find Minimum in Rotated Sorted Array' in the production database."""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from backend.db.session import AsyncSessionLocal
from backend.models.problem import Problem
from sqlalchemy import select


async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Problem).where(Problem.title == "Find Minimum in Rotated Sorted Array")
        )
        problem = res.scalar_one_or_none()
        if not problem:
            print("Problem not found!")
            return

        problem.description = (
            "Given an integer array nums of size N, sorted in ascending order with distinct values, "
            "and then rotated an unknown number of times (between 1 and N), find the minimum element in the array.\n\n"
            "**Example 1**\n\n"
            "Input: `nums = [4, 5, 6, 7, 0, 1, 2, 3]`\n\n"
            "Output: `0`\n\n"
            "Explanation: Here, the element 0 is the minimum element in the array.\n\n"
            "**Example 2**\n\n"
            "Input: `nums = [3, 4, 5, 1, 2]`\n\n"
            "Output: `1`\n\n"
            "Explanation: Here, the element 1 is the minimum element in the array.\n\n"
            "**Example 3**\n\n"
            "Input: `nums = [4, 5, 6, 7, -7, 1, 2, 3]`\n\n"
            "Output: `-7`"
        )

        problem.constraints = (
            "- `n == nums.length`\n"
            "- `1 <= n <= 10^4`\n"
            "- `-10^4 <= nums[i] <= 10^4`\n"
            "- All the integers of `nums` are unique.\n"
            "- `nums` is sorted and rotated between `1` and `n` times."
        )

        await db.commit()
        print("Done! Constraints and description updated successfully.")


if __name__ == "__main__":
    asyncio.run(main())
