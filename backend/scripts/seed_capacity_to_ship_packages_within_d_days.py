import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.binary_search_seed_utils import make_case, upsert_problem

TITLE = "Capacity To Ship Packages Within D Days"
TARGET_CASES = 593


def solve(weights: list[int], days: int) -> int:
    left, right = max(weights), sum(weights)
    answer = right
    while left <= right:
        mid = (left + right) // 2
        used_days = 1
        current = 0
        for weight in weights:
            if current + weight > mid:
                used_days += 1
                current = 0
            current += weight
        if used_days <= days:
            answer = mid
            right = mid - 1
        else:
            left = mid + 1
    return answer


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5),
        ([3, 2, 2, 4, 1, 4], 3),
        ([1, 2, 3, 1, 1], 4),
    ]
    for weights, days in samples:
        cases.append(make_case(weights, days, expected_output=solve(weights, days), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([5], 1),
        ([5], 3),
        ([10, 50, 50, 10], 2),
        ([7, 7, 7, 7], 4),
        ([7, 7, 7, 7], 1),
        ([1, 100, 1, 100, 1], 3),
        ([9, 8, 7, 6, 5], 5),
        ([9, 8, 7, 6, 5], 2),
    ]
    for weights, days in fixed:
        cases.append(make_case(weights, days, expected_output=solve(weights, days), idx=idx))
        idx += 1

    rng = random.Random(2026040208)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 220)
        weights = [rng.randint(1, 500) for _ in range(n)]
        days = rng.randint(1, n)
        cases.append(make_case(weights, days, expected_output=solve(weights, days), idx=idx))
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
                description="A conveyor belt has packages that must be shipped from one port to another within days days.\n\nThe i-th package has weight weights[i]. Each day, you load the ship with packages from the conveyor belt in the given order. The maximum load you can take in one day is the ship capacity.\n\nReturn the least weight capacity of the ship that will result in all packages being shipped within days days.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array weights\nLine 2: integer days",
                output_format="Single integer: minimum ship capacity",
                constraints="1 <= days <= weights.length <= 5 * 10^4\n1 <= weights[i] <= 500",
                method_name="shipWithinDays",
                parameters=[{"name": "weights", "type": "int[]"}, {"name": "days", "type": "int"}],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1300,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
