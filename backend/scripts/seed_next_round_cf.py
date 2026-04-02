import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TITLE = "Next Round"
TARGET_CASES = 559


def solve(scores: list[int], k: int) -> str:
    threshold = scores[k - 1]
    return str(sum(1 for score in scores if score >= threshold and score > 0))


def make_input(scores: list[int], k: int) -> str:
    return "\n".join([f"{len(scores)} {k}", " ".join(map(str, scores))])


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([10, 9, 8, 7, 7, 7, 5, 5], 5),
        ([0, 0, 0, 0], 2),
        ([100, 50, 50, 25, 10], 3),
    ]
    for scores, k in samples:
        cases.append(make_case(make_input(scores, k), solve(scores, k), idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 1),
        ([0], 1),
        ([5, 4, 3, 2, 1], 1),
        ([5, 4, 3, 2, 1], 5),
        ([9, 9, 9, 9], 4),
        ([3, 3, 0, 0, 0], 2),
        ([8, 7, 7, 7, 6, 0], 4),
        ([10, 0, 0, 0, 0], 1),
        ([10, 9, 8, 7, 6], 5),
        ([1, 1, 1, 1, 1], 3),
        ([0, 0, 0, 0, 0, 0], 6),
        ([1000, 999, 998, 0, 0, 0], 3),
        ([5, 5, 5, 5, 5, 5, 5], 7),
        ([7, 6, 5, 4, 3, 2, 1], 4),
        ([2, 2, 1, 1, 1, 0], 2),
        ([9, 8, 8, 8, 8, 8, 8, 1], 3),
        ([1, 0], 1),
        ([1, 0], 2),
    ]
    for scores, k in fixed:
        cases.append(make_case(make_input(scores, k), solve(scores, k), idx))
        idx += 1

    rng = random.Random(2026040205)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 200)
        scores = sorted([rng.randint(0, 1000) for _ in range(n)], reverse=True)
        k = rng.randint(1, n)
        cases.append(make_case(make_input(scores, k), solve(scores, k), idx))
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
                    "Contestants advance to the next round if their score is positive and at least as large "
                    "as the k-th contestant's score in the ranking list."
                ),
                difficulty=Difficulty.EASY,
                input_format="Line 1: integers n and k\nLine 2: n non-increasing scores",
                output_format="Print one integer: the number of advancing contestants.",
                constraints="1 <= k <= n <= 200\n0 <= scores[i] <= 1000",
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
