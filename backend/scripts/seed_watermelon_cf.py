import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TITLE = "Watermelon"
TARGET_CASES = 544


def solve(weight: int) -> str:
    return "YES" if weight > 2 and weight % 2 == 0 else "NO"


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [8, 5, 2]
    for weight in samples:
        cases.append(make_case(str(weight), solve(weight), idx, is_sample=True))
        idx += 1

    edge_cases = [
        1, 2, 3, 4, 5, 6,
        7, 8, 9, 10,
        17, 18, 19, 20,
        97, 98, 99, 100,
        999999, 1000000,
    ]
    for weight in edge_cases:
        cases.append(make_case(str(weight), solve(weight), idx))
        idx += 1

    rng = random.Random(2026040202)
    while len(cases) < TARGET_CASES:
        weight = rng.randint(1, 10**6)
        cases.append(make_case(str(weight), solve(weight), idx))
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
                    "You are given the weight of a watermelon. Determine whether it can be split into "
                    "two parts such that both parts have positive even weight."
                ),
                difficulty=Difficulty.EASY,
                input_format="Line 1: integer w",
                output_format='Print "YES" if such a split exists, otherwise print "NO".',
                constraints="1 <= w <= 10^6",
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
