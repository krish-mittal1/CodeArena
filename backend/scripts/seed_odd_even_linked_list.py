import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Odd Even Linked List"
TARGET_CASES = 447


def solve(values: list[int]) -> list[int]:
    odd = values[::2]
    even = values[1::2]
    return odd + even


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        [1, 2, 3, 4, 5],
        [2, 1, 3, 5, 6, 4, 7],
        [],
    ]
    for values in samples:
        cases.append(make_case(values, expected_output=solve(values), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [1, 2],
        [1, 1, 1, 1],
        [-5, -4, -3, -2, -1],
        [10, 20, 30],
        [9, 8, 7, 6, 5, 4],
        [0, 0, 0, 0, 0],
        [3, 2, 1, 0, -1, -2, -3, -4],
    ]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve(values), idx=idx))
        idx += 1

    rng = random.Random(2026040103)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 260)
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
                description="Given the head of a singly linked list, group all nodes positioned at odd indices together followed by the nodes positioned at even indices, and return the reordered list.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head",
                output_format="JSON array representing the reordered linked list",
                constraints="0 <= number of nodes <= 10^4\n-10^6 <= Node.val <= 10^6",
                method_name="oddEvenList",
                parameters=[{"name": "head", "type": "ListNode"}],
                return_type="ListNode",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1300,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
