"""
Seed script — insert/update 'Delete the element with value X'
with 200+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_delete_element_with_value_x_ll
"""

import asyncio
import json
import logging
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Delete the element with value X"


def delete_value_x(values: list[int], x: int) -> list[int]:
    """Delete first node whose value is x (linked-list semantics)."""
    for i, v in enumerate(values):
        if v == x:
            return values[:i] + values[i + 1 :]
    return values


def make_case(values: list[int], x: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps({"linkedList": values, "X": x}),
        "expected_output": json.dumps(delete_value_x(values, x)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt-style samples.
    samples = [
        ([3, 4, 5], 5),
        ([3, 4, 5], 7),
        ([3, 4, 5], 3),
    ]
    for arr, x in samples:
        cases.append(make_case(arr, x, idx, is_sample=True))
        idx += 1

    # Edge cases.
    edge_cases = [
        ([], 1),
        ([1], 1),
        ([1], 2),
        ([0], 0),
        ([-1], -1),
        ([1, 1], 1),
        ([2, 2, 2], 2),
        ([1, 2], 1),
        ([1, 2], 2),
        ([1, 2], 3),
        ([-5, -4, -3, -2, -1], -5),
        ([-5, -4, -3, -2, -1], -1),
        ([-5, -4, -3, -2, -1], 0),
        ([10**9, -10**9, 0], -10**9),
        ([7, 7, 7, 7, 7], 7),
        ([7, 7, 7, 7, 7], 8),
    ]
    for arr, x in edge_cases:
        cases.append(make_case(arr, x, idx))
        idx += 1

    # Structured deterministic cases.
    for n in [2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]:
        inc = list(range(n))
        dec = list(range(n, 0, -1))
        alt = [i if i % 2 == 0 else -i for i in range(n)]
        const = [42] * n
        patterns = [inc, dec, alt, const]

        for arr in patterns:
            x_values = [arr[0], arr[n // 2], arr[-1], 123456789]
            for x in x_values:
                cases.append(make_case(arr, x, idx))
                idx += 1

    # Deterministic randomized set to exceed 200.
    rng = random.Random(20260331)
    while len(cases) < 230:
        n = rng.randint(0, 3500)
        mode = rng.randint(0, 4)

        if mode == 0:
            arr = [rng.randint(-1000, 1000) for _ in range(n)]
        elif mode == 1:
            start = rng.randint(-50000, 50000)
            arr = [start + i for i in range(n)]
        elif mode == 2:
            arr = [rng.choice([-1, 0, 1, 2, 3, 5, 8, 13]) for _ in range(n)]
        elif mode == 3:
            arr = [rng.randint(-10**9, 10**9) for _ in range(n)]
        else:
            a, b = rng.randint(-100, 100), rng.randint(-100, 100)
            arr = [a if i % 2 == 0 else b for i in range(n)]

        if arr and rng.random() < 0.75:
            x = arr[rng.randrange(len(arr))]
        else:
            x = rng.randint(-10**9, 10**9)

        cases.append(make_case(arr, x, idx))
        idx += 1

    return cases


async def seed() -> None:
    """Create or update the 'Delete the element with value X' problem."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(Problem).filter_by(title=TITLE))
        old_problem = result.scalars().first()
        if old_problem:
            await session.delete(old_problem)
            logger.info(f"Deleted old problem: {TITLE}")

        problem = Problem(
            title=TITLE,
            description=(
                "Given the head of a singly linked list and an integer X, delete the node "
                "with value X and return the head of the modified list."
            ),
            difficulty=Difficulty.EASY,
            input_format="Object format: {linkedList: array, X: integer}",
            output_format="Array representation after deleting first node with value X",
            constraints="0 <= list length <= 10^5, -10^9 <= node values <= 10^9",
        )

        test_cases = build_test_cases()
        for order, tc in enumerate(test_cases):
            problem.test_cases.append(
                TestCase(
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    is_sample=tc["is_sample"],
                    order_index=order,
                )
            )

        session.add(problem)
        await session.commit()
        logger.info(f"✓ Seeded: {TITLE} with {len(test_cases)} test cases")


if __name__ == "__main__":
    asyncio.run(seed())