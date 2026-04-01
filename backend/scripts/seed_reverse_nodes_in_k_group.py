import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Reverse Nodes in k-Group"
TARGET_CASES = 639


def solve(values: list[int], k: int) -> list[int]:
    out = list(values)
    for start in range(0, len(out), k):
        if start + k <= len(out):
            out[start:start + k] = reversed(out[start:start + k])
    return out


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5], 2),
        ([1, 2, 3, 4, 5], 3),
        ([1], 1),
    ]
    for values, k in samples:
        cases.append(make_case(values, k, expected_output=solve(values, k), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([], 1),
        ([1, 2], 3),
        ([1, 2, 3], 1),
        ([9, 8, 7, 6], 4),
        ([5, 5, 5, 5, 5], 2),
        ([-1, -2, -3, -4, -5, -6], 3),
        ([10, 20, 30, 40, 50, 60, 70], 5),
        ([1, 0, 1, 0, 1, 0, 1, 0], 2),
    ]
    for values, k in fixed:
        cases.append(make_case(values, k, expected_output=solve(values, k), idx=idx))
        idx += 1

    rng = random.Random(2026040108)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 220)
        values = [rng.randint(-10**4, 10**4) for _ in range(n)]
        k = rng.randint(1, max(1, 20 if n == 0 else min(n + 2, 20)))
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
                description="Given the head of a linked list, reverse the nodes of the list k at a time and return the modified list. If the number of nodes is not a multiple of k, leave the remaining nodes as-is.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: JSON array of node values for head\nLine 2: integer k",
                output_format="JSON array representing the linked list after reversing every full block of size k",
                constraints="0 <= number of nodes <= 5000\n-10^4 <= Node.val <= 10^4\n1 <= k <= 5000",
                method_name="reverseKGroup",
                parameters=[{"name": "head", "type": "ListNode"}, {"name": "k", "type": "int"}],
                return_type="ListNode",
                time_limit_ms=1800,
                memory_limit_mb=256,
                rating=1600,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
