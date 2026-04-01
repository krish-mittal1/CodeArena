import asyncio
import bisect
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Successful Pairs of Spells and Potions"
TARGET_CASES = 546


def solve(spells: list[int], potions: list[int], success: int) -> list[int]:
    potions = sorted(potions)
    n = len(potions)
    answer = []
    for spell in spells:
        need = (success + spell - 1) // spell
        idx = bisect.bisect_left(potions, need)
        answer.append(n - idx)
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([5, 1, 3], [1, 2, 3, 4, 5], 7),
        ([3, 1, 2], [8, 5, 8], 16),
    ]
    for spells, potions, success in samples:
        cases.append(make_case(spells, potions, success, expected_output=solve(spells, potions, success), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], [1], 1),
        ([1], [1], 2),
        ([10, 10], [10, 10], 100),
        ([2, 4, 8], [1, 2, 3], 8),
        ([100], [1, 1, 1, 1], 99),
        ([7, 14], [3, 6, 9], 42),
        ([5, 6, 7], [8, 9], 100),
        ([1, 2, 3, 4], [10, 20, 30, 40], 60),
    ]
    for spells, potions, success in fixed:
        cases.append(make_case(spells, potions, success, expected_output=solve(spells, potions, success), idx=idx))
        idx += 1

    rng = random.Random(2026040211)
    while len(cases) < TARGET_CASES:
        ns = rng.randint(1, 120)
        np = rng.randint(1, 120)
        spells = [rng.randint(1, 10**5) for _ in range(ns)]
        potions = [rng.randint(1, 10**5) for _ in range(np)]
        success = rng.randint(1, 10**10)
        cases.append(make_case(spells, potions, success, expected_output=solve(spells, potions, success), idx=idx))
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
                description="You are given two positive integer arrays spells and potions, where spells[i] represents the strength of the i-th spell and potions[j] represents the strength of the j-th potion.\n\nYou are also given an integer success. A spell and potion pair is considered successful if their product is at least success.\n\nReturn an integer array where the i-th element is the number of potions that will form a successful pair with the i-th spell.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array spells\nLine 2: JSON array potions\nLine 3: integer success",
                output_format="JSON array answer",
                constraints="1 <= spells.length, potions.length <= 10^5\n1 <= spells[i], potions[i] <= 10^5\n1 <= success <= 10^10",
                method_name="successfulPairs",
                parameters=[{"name": "spells", "type": "int[]"}, {"name": "potions", "type": "int[]"}, {"name": "success", "type": "long"}],
                return_type="int[]",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
