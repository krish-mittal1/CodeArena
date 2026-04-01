import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Minimum Number of Days to Make m Bouquets"
TARGET_CASES = 571


def solve(bloom_day: list[int], m: int, k: int) -> int:
    if m * k > len(bloom_day):
        return -1

    def can_make(day: int) -> bool:
        flowers = 0
        bouquets = 0
        for value in bloom_day:
            if value <= day:
                flowers += 1
                if flowers == k:
                    bouquets += 1
                    flowers = 0
            else:
                flowers = 0
        return bouquets >= m

    left, right = min(bloom_day), max(bloom_day)
    answer = right
    while left <= right:
        mid = (left + right) // 2
        if can_make(mid):
            answer = mid
            right = mid - 1
        else:
            left = mid + 1
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 10, 3, 10, 2], 3, 1),
        ([1, 10, 3, 10, 2], 3, 2),
        ([7, 7, 7, 7, 12, 7, 7], 2, 3),
    ]
    for bloom_day, m, k in samples:
        cases.append(make_case(bloom_day, m, k, expected_output=solve(bloom_day, m, k), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 1, 1),
        ([5, 5, 5], 1, 3),
        ([5, 5, 5], 2, 2),
        ([100, 1, 100, 1, 100], 2, 1),
        ([9, 8, 7, 6, 5, 4], 2, 2),
        ([1, 2, 4, 9, 3, 4, 1], 2, 2),
        ([1, 10, 2, 9, 3, 8, 4, 7], 3, 2),
        ([2, 2, 2, 2], 2, 2),
    ]
    for bloom_day, m, k in fixed:
        cases.append(make_case(bloom_day, m, k, expected_output=solve(bloom_day, m, k), idx=idx))
        idx += 1

    rng = random.Random(2026040209)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 200)
        bloom_day = [rng.randint(1, 10**4) for _ in range(n)]
        k = rng.randint(1, min(8, n))
        m = rng.randint(1, max(1, n))
        cases.append(make_case(bloom_day, m, k, expected_output=solve(bloom_day, m, k), idx=idx))
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
                description="You are given an integer array bloomDay, an integer m and an integer k.\n\nYou want to make m bouquets. To make a bouquet, you need to use k adjacent flowers from the garden.\n\nThe garden consists of n flowers, where the i-th flower will bloom on the bloomDay[i] day and then can be used in exactly one bouquet.\n\nReturn the minimum number of days you need to wait to be able to make m bouquets. If it is impossible, return -1.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array bloomDay\nLine 2: integer m\nLine 3: integer k",
                output_format="Single integer: minimum day or -1",
                constraints="1 <= bloomDay.length <= 10^5\n1 <= bloomDay[i] <= 10^9\n1 <= m <= 10^6\n1 <= k <= bloomDay.length",
                method_name="minDays",
                parameters=[{"name": "bloomDay", "type": "int[]"}, {"name": "m", "type": "int"}, {"name": "k", "type": "int"}],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1350,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
