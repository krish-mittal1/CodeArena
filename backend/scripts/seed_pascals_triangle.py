import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Pascal's Triangle"
TARGET_CASES = 523


def solve(num_rows: int) -> list[list[int]]:
    triangle: list[list[int]] = []
    for row_idx in range(num_rows):
        row = [1] * (row_idx + 1)
        for j in range(1, row_idx):
            row[j] = triangle[row_idx - 1][j - 1] + triangle[row_idx - 1][j]
        triangle.append(row)
    return triangle


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for num_rows in (5, 1, 2):
        cases.append(make_case(num_rows, expected_output=solve(num_rows), idx=idx, is_sample=True))
        idx += 1

    for num_rows in (3, 4, 6, 7, 10, 12, 15, 18):
        cases.append(make_case(num_rows, expected_output=solve(num_rows), idx=idx))
        idx += 1

    rng = random.Random(2026040206)
    while len(cases) < TARGET_CASES:
        num_rows = rng.randint(1, 25)
        cases.append(make_case(num_rows, expected_output=solve(num_rows), idx=idx))
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
                description="Given an integer numRows, return the first numRows of Pascal's triangle.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: integer numRows",
                output_format="JSON 2D array containing Pascal's triangle",
                constraints="1 <= numRows <= 25",
                method_name="generate",
                parameters=[{"name": "numRows", "type": "int"}],
                return_type="int[][]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=900,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
