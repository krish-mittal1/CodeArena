import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Delete the Middle Node of a Linked List"
TARGET_CASES = 431


def solve(values: list[int]) -> list[int]:
    if len(values) <= 1:
        return []
    mid = len(values) // 2
    return values[:mid] + values[mid + 1 :]


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        [1, 3, 4, 7, 1, 2, 6],
        [1, 2, 3, 4],
        [2, 1],
    ]
    for values in samples:
        cases.append(make_case(values, expected_output=solve(values), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1],
        [9, 9, 9],
        [5, 4, 3, 2, 1],
        [-3, -2, -1, 0, 1, 2],
        [1, 2],
        [10, 20, 30, 40, 50, 60, 70, 80],
        [0, 0, 0, 0],
        [7, 6, 5, 4, 3, 2, 1],
    ]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve(values), idx=idx))
        idx += 1

    rng = random.Random(2026040106)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 280)
        values = [rng.randint(-10**5, 10**5) for _ in range(n)]
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
                description="You are given the head of a linked list. Delete the middle node and return the head of the modified linked list. For an even number of nodes, the second middle node is considered the middle.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head",
                output_format="JSON array representing the linked list after removing the middle node",
                constraints="1 <= number of nodes <= 10^5\n1 <= Node.val <= 10^5",
                method_name="deleteMiddle",
                parameters=[{"name": "head", "type": "ListNode"}],
                return_type="ListNode",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1275,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
