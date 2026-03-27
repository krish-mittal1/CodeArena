import asyncio
import json
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

def generate_test_cases():
    cases = []
    
    # Preset sample cases
    cases.append({"input": json.dumps([1, 0, 2, 1, 0]), "expected_output": json.dumps([0, 0, 1, 1, 2]), "is_sample": True})
    cases.append({"input": json.dumps([0, 0, 1, 1, 1]), "expected_output": json.dumps([0, 0, 1, 1, 1]), "is_sample": True})
    cases.append({"input": json.dumps([2, 0, 1]), "expected_output": json.dumps([0, 1, 2]), "is_sample": True})
    
    # Edge cases
    cases.append({"input": json.dumps([]), "expected_output": json.dumps([]), "is_sample": False})
    cases.append({"input": json.dumps([0]), "expected_output": json.dumps([0]), "is_sample": False})
    cases.append({"input": json.dumps([1]), "expected_output": json.dumps([1]), "is_sample": False})
    cases.append({"input": json.dumps([2]), "expected_output": json.dumps([2]), "is_sample": False})
    
    cases.append({"input": json.dumps([0,0,0,0]), "expected_output": json.dumps([0,0,0,0]), "is_sample": False})
    cases.append({"input": json.dumps([1,1,1,1]), "expected_output": json.dumps([1,1,1,1]), "is_sample": False})
    cases.append({"input": json.dumps([2,2,2,2]), "expected_output": json.dumps([2,2,2,2]), "is_sample": False})
    
    # Already sorted
    for length in [10, 50, 100]:
        arr = sorted(random.choices([0,1,2], k=length))
        cases.append({"input": json.dumps(arr), "expected_output": json.dumps(arr), "is_sample": False})
    
    # Reverse sorted
    for length in [10, 50, 100]:
        arr = sorted(random.choices([0,1,2], k=length), reverse=True)
        cases.append({"input": json.dumps(arr), "expected_output": json.dumps(sorted(arr)), "is_sample": False})
    
    # Random cases to reach 150+
    random.seed(42)
    while len(cases) < 155:
        length = random.randint(5, 1000)
        arr = random.choices([0, 1, 2], k=length)
        cases.append({"input": json.dumps(arr), "expected_output": json.dumps(sorted(arr)), "is_sample": False})
        
    for i, c in enumerate(cases):
        c["order_index"] = i
        
    return cases

async def seed():
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as ds:
        title = "Sort an array of 0's 1's and 2's"
        
        # Determine problem
        res = await ds.execute(select(Problem).where(Problem.title == title))
        problem = res.scalars().first()
        
        if problem:
            logger.info("Problem already exists, updating...")
            problem.description = "Given an array `nums` consisting of only 0, 1, or 2. Sort the array in non-decreasing order.\n\nThe sorting must be done in-place, without making a copy of the original array.\n\n**Note for this platform:** Even though the algorithm is in-place, our execution engine requires your function to **return the modified array** `nums`."
            problem.difficulty = Difficulty.MEDIUM
            problem.input_format = "A JSON array `nums` of integers (0, 1, or 2)."
            problem.output_format = "A JSON array representing the sorted `nums`."
            problem.constraints = "1 <= nums.length <= 10^5\nnums[i] is either 0, 1, or 2."
            problem.method_name = "sortColors"
            problem.parameters = [{"name": "nums", "type": "int[]"}]
            problem.return_type = "int[]"
        else:
            logger.info("Creating new problem...")
            problem = Problem(
                title=title,
                description="Given an array `nums` consisting of only 0, 1, or 2. Sort the array in non-decreasing order.\n\nThe sorting must be done in-place, without making a copy of the original array.\n\n**Note for this platform:** Even though the algorithm is in-place, our execution engine requires your function to **return the modified array** `nums`.",
                difficulty=Difficulty.MEDIUM,
                input_format="A JSON array `nums` of integers (0, 1, or 2).",
                output_format="A JSON array representing the sorted `nums`.",
                constraints="1 <= nums.length <= 10^5\nnums[i] is either 0, 1, or 2.",
                method_name="sortColors",
                parameters=[{"name": "nums", "type": "int[]"}],
                return_type="int[]",
                rating=1000
            )
            ds.add(problem)
            await ds.flush()
            
        # Delete old test cases
        await ds.execute(select(TestCase).where(TestCase.problem_id == problem.id))
        
        # Re-fetch problem to avoid DetachedInstanceError when setting test_cases implicitly
        # Actually it's easier to just issue delete then add objects.
        # Wait, the relationship might have old items. 
        # Using simple cascade works when deleting the parent, but here we just delete the children explicitly.
        
        test_cases_data = generate_test_cases()
        logger.info(f"Generated {len(test_cases_data)} test cases.")
        
        for data in test_cases_data:
            tc = TestCase(
                problem_id=problem.id,
                input=data["input"],
                expected_output=data["expected_output"],
                is_sample=data.get("is_sample", False),
                order_index=data.get("order_index", 0)
            )
            ds.add(tc)
            
        await ds.commit()
        logger.info(f"Successfully seeded/updated problem '{title}' with {len(test_cases_data)} test cases.")

if __name__ == "__main__":
    asyncio.run(seed())
