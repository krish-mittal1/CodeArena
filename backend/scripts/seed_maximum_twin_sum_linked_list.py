import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Maximum Twin Sum of a Linked List"
TARGET_CASES = 557


def solve(values: list[int]) -> int:
    best = 0
    n = len(values)
    for i in range(n // 2):
        best = max(best, values[i] + values[n - 1 - i])
    return best


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        [5, 4, 2, 1],
        [4, 2, 2, 3],
        [1, 100000],
    ]
    for values in samples:
        cases.append(make_case(values, expected_output=solve(values), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [1, 1],
        [9, 0, 0, 9],
        [1, 2, 3, 4, 5, 6],
        [100000, 1, 1, 100000],
        [7, 7, 7, 7, 7, 7],
        [3, 8, 1, 9, 2, 7, 4, 6],
        [0, 0, 0, 0],
        [11, 22, 33, 44, 55, 66, 77, 88, 99, 111],
    ]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve(values), idx=idx))
        idx += 1

    rng = random.Random(2026040107)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 130) * 2
        values = [rng.randint(0, 100000) for _ in range(n)]
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
                description="In a linked list of even length, the twin of the ith node is the (n - 1 - i)th node. Return the maximum twin sum of the linked list.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array of node values for head",
                output_format="Single integer representing the maximum twin sum",
                constraints="2 <= number of nodes <= 10^5\nThe number of nodes is even.\n1 <= Node.val <= 10^5",
                method_name="pairSum",
                parameters=[{"name": "head", "type": "ListNode"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1400,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
