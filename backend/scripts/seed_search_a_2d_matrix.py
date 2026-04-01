import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Search a 2D Matrix"
TARGET_CASES = 528


def solve(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1
    while left <= right:
        mid = (left + right) // 2
        value = matrix[mid // cols][mid % cols]
        if value == target:
            return True
        if value < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


def build_matrix(rows: int, cols: int, start: int, step: int) -> list[list[int]]:
    values = [start + step * i for i in range(rows * cols)]
    return [values[r * cols:(r + 1) * cols] for r in range(rows)]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3),
        ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13),
    ]
    for matrix, target in samples:
        cases.append(make_case(matrix, target, expected_output=solve(matrix, target), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([[1]], 1),
        ([[1]], 2),
        ([[1, 3, 5]], 5),
        ([[1], [3], [5]], 4),
        ([[1, 2], [3, 4]], 4),
        ([[1, 2], [3, 4]], 0),
        ([[-10, -5, -1], [2, 7, 11]], -5),
        ([[-10, -5, -1], [2, 7, 11]], 6),
    ]
    for matrix, target in fixed:
        cases.append(make_case(matrix, target, expected_output=solve(matrix, target), idx=idx))
        idx += 1

    rng = random.Random(2026040205)
    while len(cases) < TARGET_CASES:
        rows = rng.randint(1, 30)
        cols = rng.randint(1, 30)
        matrix = build_matrix(rows, cols, rng.randint(-5000, 5000), rng.randint(1, 9))
        flat = [value for row in matrix for value in row]
        target = rng.choice(flat) if rng.random() < 0.7 else rng.randint(flat[0] - 20, flat[-1] + 20)
        cases.append(make_case(matrix, target, expected_output=solve(matrix, target), idx=idx))
        idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        await upsert_problem(
            db,
            TITLE,
            dict(
                description="You are given an m x n integer matrix with the following two properties:\n\n1. Each row is sorted in non-decreasing order.\n2. The first integer of each row is greater than the last integer of the previous row.\n\nGiven an integer target, return true if target is in matrix or false otherwise.\n\nYou must write a solution in O(log(m * n)) time complexity.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON matrix matrix\nLine 2: integer target",
                output_format="Boolean true/false",
                constraints="1 <= m, n <= 100\n-10^9 <= matrix[i][j], target <= 10^9",
                method_name="searchMatrix",
                parameters=[{"name": "matrix", "type": "int[][]"}, {"name": "target", "type": "int"}],
                return_type="boolean",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
