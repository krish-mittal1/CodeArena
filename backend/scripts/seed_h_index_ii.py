import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "H-Index II"
TARGET_CASES = 509


def solve(citations: list[int]) -> int:
    n = len(citations)
    left, right = 0, n - 1
    answer = 0
    while left <= right:
        mid = (left + right) // 2
        h = n - mid
        if citations[mid] >= h:
            answer = h
            right = mid - 1
        else:
            left = mid + 1
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [[0, 1, 3, 5, 6], [1, 2, 100]]
    for citations in samples:
        cases.append(make_case(citations, expected_output=solve(citations), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [0],
        [100],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 1, 2, 3, 4, 5],
        [0, 0, 4, 4],
        [0, 2, 4, 4, 4],
        [5, 5, 5, 5, 5],
    ]
    for citations in fixed:
        cases.append(make_case(citations, expected_output=solve(citations), idx=idx))
        idx += 1

    rng = random.Random(2026040210)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 260)
        citations = sorted(rng.randint(0, 1000) for _ in range(n))
        cases.append(make_case(citations, expected_output=solve(citations), idx=idx))
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
                description="Given an array of integers citations where citations[i] is the number of citations a researcher received for their i-th paper and citations is sorted in ascending order, return the researcher's h-index.\n\nThe h-index is defined as the maximum value h such that the researcher has at least h papers with at least h citations each.\n\nYou must write an algorithm that runs in logarithmic time.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array citations",
                output_format="Single integer: h-index",
                constraints="1 <= citations.length <= 10^5\n0 <= citations[i] <= 1000\ncitations is sorted in ascending order.",
                method_name="hIndex",
                parameters=[{"name": "citations", "type": "int[]"}],
                return_type="int",
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
