import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Rotate List"
TARGET_CASES = 611


def solve(values: list[int], k: int) -> list[int]:
    if not values:
        return []
    shift = k % len(values)
    if shift == 0:
        return list(values)
    return values[-shift:] + values[:-shift]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5], 2),
        ([0, 1, 2], 4),
        ([], 0),
    ]
    for values, k in samples:
        cases.append(make_case(values, k, expected_output=solve(values, k), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 0),
        ([1], 99),
        ([1, 2], 1),
        ([1, 2], 2),
        ([5, 5, 5], 7),
        ([-1, -2, -3, -4], 3),
        ([9, 8, 7, 6, 5], 10),
        ([1, 0, 1, 0, 1, 0], 5),
    ]
    for values, k in fixed:
        cases.append(make_case(values, k, expected_output=solve(values, k), idx=idx))
        idx += 1

    rng = random.Random(2026040105)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 260)
        values = [rng.randint(-10**4, 10**4) for _ in range(n)]
        k = rng.randint(0, 5000)
        cases.append(make_case(values, k, expected_output=solve(values, k), idx=idx))
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
                description="Given the head of a linked list, rotate the list to the right by k places and return the new head.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head\nLine 2: integer k",
                output_format="JSON array representing the rotated linked list",
                constraints="0 <= number of nodes <= 500\n-100 <= Node.val <= 100\n0 <= k <= 2 * 10^9",
                method_name="rotateRight",
                parameters=[{"name": "head", "type": "ListNode"}, {"name": "k", "type": "int"}],
                return_type="ListNode",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1350,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
