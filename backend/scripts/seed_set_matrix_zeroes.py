import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Set Matrix Zeroes"
TARGET_CASES = 608


def solve(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix:
        return []
    rows = {r for r, row in enumerate(matrix) for value in row if value == 0}
    cols = {c for c in range(len(matrix[0])) for r in range(len(matrix)) if matrix[r][c] == 0}
    out = [row[:] for row in matrix]
    for r in range(len(out)):
        for c in range(len(out[0])):
            if r in rows or c in cols:
                out[r][c] = 0
    return out


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for matrix in (
        [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
        [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],
        [[1]],
    ):
        cases.append(make_case(matrix, expected_output=solve(matrix), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [[0]],
        [[1, 2, 3]],
        [[1], [0], [3]],
        [[1, 2], [3, 4]],
        [[1, 0], [0, 1]],
        [[5, 6, 7], [8, 9, 10], [0, 12, 13]],
        [[0, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[1, 2, 3], [4, 5, 0], [7, 8, 9], [10, 11, 12]],
    ]
    for matrix in fixed:
        cases.append(make_case(matrix, expected_output=solve(matrix), idx=idx))
        idx += 1

    rng = random.Random(2026040209)
    while len(cases) < TARGET_CASES:
        rows = rng.randint(1, 25)
        cols = rng.randint(1, 25)
        matrix = [[rng.randint(-50, 50) for _ in range(cols)] for _ in range(rows)]
        for _ in range(rng.randint(0, max(1, rows * cols // 8))):
            matrix[rng.randrange(rows)][rng.randrange(cols)] = 0
        cases.append(make_case(matrix, expected_output=solve(matrix), idx=idx))
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
                description="Given an m x n integer matrix, if an element is 0, set its entire row and column to 0.\n\nOn this platform, return the final matrix after applying the in-place transformation.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON 2D array matrix",
                output_format="JSON 2D array after setting rows and columns to zero",
                constraints="1 <= matrix.length, matrix[0].length <= 25\n-2^31 <= matrix[i][j] <= 2^31 - 1",
                method_name="setZeroes",
                parameters=[{"name": "matrix", "type": "int[][]"}],
                return_type="int[][]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1250,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
