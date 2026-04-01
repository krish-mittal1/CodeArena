import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Partition List"
TARGET_CASES = 582


def solve(values: list[int], x: int) -> list[int]:
    lower = [value for value in values if value < x]
    higher = [value for value in values if value >= x]
    return lower + higher


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 4, 3, 2, 5, 2], 3),
        ([2, 1], 2),
        ([], 5),
    ]
    for values, x in samples:
        cases.append(make_case(values, x, expected_output=solve(values, x), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 0),
        ([1], 2),
        ([3, 3, 3], 3),
        ([5, 4, 3, 2, 1], 3),
        ([-3, -1, -2, 0, 2], -1),
        ([1, 2, 3, 4], 10),
        ([10, 9, 8], -5),
        ([2, 1, 2, 1, 2, 1], 2),
    ]
    for values, x in fixed:
        cases.append(make_case(values, x, expected_output=solve(values, x), idx=idx))
        idx += 1

    rng = random.Random(2026040104)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 240)
        values = [rng.randint(-10**4, 10**4) for _ in range(n)]
        x = rng.randint(-10**4, 10**4)
        cases.append(make_case(values, x, expected_output=solve(values, x), idx=idx))
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
                description="Given the head of a linked list and a value x, partition it so that all nodes less than x come before nodes greater than or equal to x while preserving the original relative order in each partition.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head\nLine 2: integer x",
                output_format="JSON array representing the partitioned linked list",
                constraints="0 <= number of nodes <= 300\n-10^4 <= Node.val <= 10^4\n-10^4 <= x <= 10^4",
                method_name="partition",
                parameters=[{"name": "head", "type": "ListNode"}, {"name": "x", "type": "int"}],
                return_type="ListNode",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1325,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
