import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Best Time to Buy and Sell Stock"
TARGET_CASES = 534


def solve(prices: list[int]) -> int:
    best = 0
    low = prices[0]
    for price in prices[1:]:
        best = max(best, price - low)
        low = min(low, price)
    return best


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for prices in ([7, 1, 5, 3, 6, 4], [7, 6, 4, 3, 1], [2, 4, 1]):
        cases.append(make_case(prices, expected_output=solve(prices), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [5],
        [1, 2],
        [2, 1],
        [3, 3, 3, 3],
        [1, 10, 2, 9],
        [9, 1, 9, 1, 9],
        [8, 6, 5, 4, 7],
        [2, 1, 2, 0, 1],
    ]
    for prices in fixed:
        cases.append(make_case(prices, expected_output=solve(prices), idx=idx))
        idx += 1

    rng = random.Random(2026040202)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 500)
        prices = [rng.randint(0, 10**5) for _ in range(n)]
        cases.append(make_case(prices, expected_output=solve(prices), idx=idx))
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
                description="You are given an array prices where prices[i] is the price of a given stock on the ith day.\n\nYou want to maximize your profit by choosing a single day to buy one stock and choosing a different future day to sell that stock.\nReturn the maximum profit you can achieve. If you cannot achieve any profit, return 0.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: JSON array prices",
                output_format="Single integer: maximum profit",
                constraints="1 <= prices.length <= 500\n0 <= prices[i] <= 10^5",
                method_name="maxProfit",
                parameters=[{"name": "prices", "type": "int[]"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=950,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
