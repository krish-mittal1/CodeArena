import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Swap Nodes in Pairs"
TARGET_CASES = 523


def solve(values: list[int]) -> list[int]:
    out = list(values)
    for i in range(0, len(out) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return out


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        [1, 2, 3, 4],
        [],
        [1],
    ]
    for values in samples:
        cases.append(make_case(values, expected_output=solve(values), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1, 2],
        [1, 2, 3],
        [7, 7, 7, 7],
        [-3, -2, -1, 0, 1],
        [10],
        [5, 4, 3, 2, 1],
        [8, 9, 10, 11, 12, 13],
        [42, 42, 42],
    ]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve(values), idx=idx))
        idx += 1

    rng = random.Random(2026040102)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 220)
        values = [rng.randint(-10**4, 10**4) for _ in range(n)]
        cases.append(make_case(values, expected_output=solve(values), idx=idx))
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
                description="Given a linked list, swap every two adjacent nodes and return its head. You must solve the problem without modifying the values stored in the list nodes.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head",
                output_format="JSON array representing the linked list after every adjacent pair is swapped",
                constraints="0 <= number of nodes <= 300\n-10^4 <= Node.val <= 10^4",
                method_name="swapPairs",
                parameters=[{"name": "head", "type": "ListNode"}],
                return_type="ListNode",
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
