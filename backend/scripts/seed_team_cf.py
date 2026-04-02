import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TITLE = "Team"
TARGET_CASES = 547


def solve(rows: list[tuple[int, int, int]]) -> str:
    return str(sum(1 for row in rows if sum(row) >= 2))


def make_input(rows: list[tuple[int, int, int]]) -> str:
    return "\n".join([str(len(rows)), *[" ".join(map(str, row)) for row in rows]])


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        [(1, 1, 0), (1, 1, 1), (1, 0, 0)],
        [(0, 0, 0)],
        [(1, 1, 1), (0, 1, 1)],
    ]
    for rows in samples:
        cases.append(make_case(make_input(rows), solve(rows), idx, is_sample=True))
        idx += 1

    fixed = [
        [(1, 0, 1)],
        [(0, 0, 0)],
        [(1, 1, 0)],
        [(1, 1, 1)],
        [(0, 1, 0), (0, 1, 1)],
        [(1, 1, 0)] * 10,
        [(0, 0, 1)] * 8,
        [(1, 1, 1), (1, 1, 1), (1, 1, 1)],
        [(0, 0, 0)] * 25,
        [(1, 0, 1)] * 25,
        [(1, 1, 0), (1, 0, 0), (0, 1, 1), (0, 0, 1)],
        [(1, 0, 0), (0, 1, 0), (0, 0, 1)],
        [(1, 1, 0), (1, 1, 0), (0, 0, 0), (1, 1, 1)],
        [(1, 0, 1), (1, 0, 1), (0, 1, 0), (0, 1, 1)],
        [(1, 1, 1)] * 150,
    ]
    for rows in fixed:
        cases.append(make_case(make_input(rows), solve(rows), idx))
        idx += 1

    rng = random.Random(2026040204)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 150)
        rows = [
            (rng.randint(0, 1), rng.randint(0, 1), rng.randint(0, 1))
            for _ in range(n)
        ]
        cases.append(make_case(make_input(rows), solve(rows), idx))
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
                description=(
                    "A team of three friends will solve a problem only if at least two of them are sure "
                    "about the solution. Count how many problems they will solve."
                ),
                difficulty=Difficulty.EASY,
                input_format="Line 1: integer n\nNext n lines: three integers 0 or 1",
                output_format="Print one integer: the number of problems the team solves.",
                constraints="1 <= n <= 150",
                problem_type="cp",
                time_limit_ms=1000,
                memory_limit_mb=256,
                rating=800,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
