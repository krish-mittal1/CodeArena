import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.linked_list_seed_utils import make_case, upsert_problem

TITLE = "Add Two Numbers"
TARGET_CASES = 468


def solve(a: list[int], b: list[int]) -> list[int]:
    i = 0
    carry = 0
    out: list[int] = []
    while i < len(a) or i < len(b) or carry:
        total = carry
        if i < len(a):
            total += a[i]
        if i < len(b):
            total += b[i]
        out.append(total % 10)
        carry = total // 10
        i += 1
    return out


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ([2, 4, 3], [5, 6, 4]),
        ([0], [0]),
        ([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]),
    ]
    for a, b in samples:
        cases.append(make_case(a, b, expected_output=solve(a, b), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], [9]),
        ([9], [1]),
        ([5], [5]),
        ([0, 0, 0], [0]),
        ([1, 8], [0]),
        ([9, 9, 9], [1]),
        ([2, 4, 9], [5, 6, 4, 9]),
        ([1, 0, 0, 0, 0, 0, 1], [5, 6, 4]),
    ]
    for a, b in fixed:
        cases.append(make_case(a, b, expected_output=solve(a, b), idx=idx))
        idx += 1

    rng = random.Random(2026040101)
    while len(cases) < TARGET_CASES:
        n1 = rng.randint(1, 140)
        n2 = rng.randint(1, 140)
        a = [rng.randint(0, 9) for _ in range(n1)]
        b = [rng.randint(0, 9) for _ in range(n2)]
        cases.append(make_case(a, b, expected_output=solve(a, b), idx=idx))
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
                description="You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each node contains a single digit. Add the two numbers and return the sum as a linked list.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array for l1 digits in reverse order\nLine 2: JSON array for l2 digits in reverse order",
                output_format="JSON array representing the resulting linked list in reverse order",
                constraints="1 <= l1.length, l2.length <= 150\n0 <= Node.val <= 9\nThe numbers do not contain leading zeroes except the number 0 itself.",
                method_name="addTwoNumbers",
                parameters=[{"name": "l1", "type": "ListNode"}, {"name": "l2", "type": "ListNode"}],
                return_type="ListNode",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
