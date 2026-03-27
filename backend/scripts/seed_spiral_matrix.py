"""
Seed script — insert 'Print the matrix in spiral manner' problem with 100+ test cases.

Usage: python -m backend.scripts.seed_spiral_matrix
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

def solve_spiral(matrix):
    if not matrix or not matrix[0]:
        return []
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            res.append(matrix[top][j])
        top += 1
        
        for i in range(top, bottom + 1):
            res.append(matrix[i][right])
        right -= 1
        
        if top <= bottom:
            for j in range(right, left - 1, -1):
                res.append(matrix[bottom][j])
            bottom -= 1
            
        if left <= right:
            for i in range(bottom, top - 1, -1):
                res.append(matrix[i][left])
            left += 1
            
    return res

def generate_matrix(rows, cols):
    return [[random.randint(-1000, 1000) for _ in range(cols)] for _ in range(rows)]

def build_test_case(matrix, is_sample=False, order_index=0):
    rows = len(matrix)
    cols = len(matrix[0])
    
    input_str = f"{rows} {cols}\n"
    for r in matrix:
        input_str += " ".join(map(str, r)) + "\n"
        
    expected_list = solve_spiral(matrix)
    output_str = " ".join(map(str, expected_list))
    
    return {
        "input": input_str.strip(),
        "expected_output": output_str,
        "is_sample": is_sample,
        "order_index": order_index
    }

async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # 1. Delete old overlapping problems
        targets = ["Print the matrix in spiral manner", "Spiral Printer", "Spiral Matrix"]
        result = await db.execute(select(Problem).where(Problem.title.in_(targets)))
        old_probs = list(result.scalars().all())
        for op in old_probs:
            logger.info(f"Removing old problem: {op.title}")
            await db.delete(op)
        await db.commit()

        # 2. Create the new problem
        problem_data = {
            "title": "Print the matrix in spiral manner",
            "difficulty": Difficulty.MEDIUM,
            "rating": 1100,
            "description": "Given an M * N matrix, print the elements in a clockwise spiral manner.\n\nReturn an array with the elements in the order of their appearance when printed in a spiral manner.",
            "input_format": "First line contains two integers M and N.\nNext M lines contain N integers each.",
            "output_format": "Print all elements space-separated in clockwise spiral order.",
            "constraints": "1 <= M, N <= 100\n-1000 <= matrix[i][j] <= 1000",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
        }
        
        problem = Problem(**problem_data)
        db.add(problem)
        await db.flush()

        logger.info(f"Created Problem: {problem.title} (ID: {problem.id})")

        # 3. Generate 100+ Test Cases
        test_cases_data = []
        idx = 0
        
        # Sample 1 (from description)
        tc1_m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        test_cases_data.append(build_test_case(tc1_m, True, idx))
        idx += 1
        
        # Sample 2 (from description)
        tc2_m = [[1, 2, 3, 4], [5, 6, 7, 8]]
        test_cases_data.append(build_test_case(tc2_m, True, idx))
        idx += 1
        
        # Additional edge cases manually created
        test_cases_data.append(build_test_case([[42]], False, idx)); idx += 1 # 1x1
        test_cases_data.append(build_test_case([[1, 2, 3, 4, 5]], False, idx)); idx += 1 # 1xN
        test_cases_data.append(build_test_case([[1], [2], [3], [4]], False, idx)); idx += 1 # Mx1
        test_cases_data.append(build_test_case([[1, 2], [3, 4]], False, idx)); idx += 1 # 2x2
        
        # Procedurally generate 100 more random matrices of varying sizes
        sizes = [
            (2, 3), (3, 2), (5, 5), (10, 10), (20, 20), (50, 50),
            (10, 1), (1, 10), (100, 1), (1, 100), (33, 17), (18, 55)
        ]
        # Generate some completely random ones
        for _ in range(90):
            r = random.randint(1, 100)
            c = random.randint(1, 100)
            if r * c > 10000: # clamp to avoid massive testcases causing issues
                c = 10000 // r
            sizes.append((max(1, r), max(1, c)))
            
        for r, c in sizes:
            mat = generate_matrix(r, c)
            test_cases_data.append(build_test_case(mat, False, idx))
            idx += 1

        for tc in test_cases_data:
            db.add(TestCase(problem_id=problem.id, **tc))
            
        await db.commit()
        logger.info(f"✅ Successfully seeded {idx} test cases for 'Print the matrix in spiral manner'.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
