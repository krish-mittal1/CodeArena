import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TITLE = "Helpful Maths"
TARGET_CASES = 509


def solve(expression: str) -> str:
    parts = expression.split("+")
    parts.sort()
    return "+".join(parts)


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = ["3+2+1", "1+1+3+1+3", "2"]
    for expression in samples:
        cases.append(make_case(expression, solve(expression), idx, is_sample=True))
        idx += 1

    fixed = [
        "1+2+3",
        "3+3+3",
        "2+1",
        "1",
        "+".join(["3"] * 20),
        "+".join(["2", "1", "2", "3", "1", "3", "2"]),
    ]
    for expression in fixed:
        cases.append(make_case(expression, solve(expression), idx))
        idx += 1

    rng = random.Random(2026040206)
    while len(cases) < TARGET_CASES:
        length = rng.randint(1, 120)
        expression = "+".join(str(rng.randint(1, 3)) for _ in range(length))
        cases.append(make_case(expression, solve(expression), idx))
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
                    "You are given a sum of single-digit numbers 1, 2, and 3 joined by plus signs. "
                    "Reorder the numbers so the resulting expression is in non-decreasing order."
                ),
                difficulty=Difficulty.EASY,
                input_format='Line 1: a string like "3+2+1"',
                output_format="Print the reordered expression.",
                constraints="The expression contains 1 to 120 numbers.\nEach number is one of 1, 2, or 3.",
                problem_type="cp",
                time_limit_ms=1000,
                memory_limit_mb=256,
                rating=900,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
