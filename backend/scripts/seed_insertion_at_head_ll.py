"""
Seed script - insert/update 'Insertion at the head of Linked List'
with 200+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_insertion_at_head_ll
"""

import asyncio
import json
import logging
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Insertion at the head of Linked List"


def insert_head(values: list[int], x: int) -> list[int]:
    """Reference solver using array form of linked-list values."""
    return [x] + values


def make_case(values: list[int], x: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps({"linkedList": values, "X": x}),
        "expected_output": json.dumps(insert_head(values, x)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt-style samples.
    samples = [
        ([1, 2, 3], 7),
        ([], 7),
        ([1, 3], 4),
    ]
    for arr, x in samples:
        cases.append(make_case(arr, x, idx, is_sample=True))
        idx += 1

    # Edge cases.
    edge_cases = [
        ([], 0),
        ([], -1),
        ([1], 1),
        ([1], 2),
        ([0], 0),
        ([-1], -1),
        ([10**9], -10**9),
        ([-10**9], 10**9),
        ([5, 5], 5),
        ([7, 7, 7, 7], 7),
        ([-5, -4, -3, -2, -1], -6),
        ([-5, -4, -3, -2, -1], 100),
        ([1, -1, 1, -1], 0),
        ([42] * 20, 42),
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
        for arr in [inc, dec, alt, const]:
            for x in [arr[0], arr[-1], 0, -999999, 999999]:
                cases.append(make_case(arr, x, idx))
                idx += 1

    # Deterministic randomized set to exceed 200.
    rng = random.Random(20260331)
    while len(cases) < 230:
        n = rng.randint(0, 3000)
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

        x = rng.randint(-10**9, 10**9)
        cases.append(make_case(arr, x, idx))
        idx += 1

    return cases


async def seed() -> None:
    """Create or update the 'Insertion at the head of Linked List' problem."""
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
                "Given the head of a singly linked list and an integer X, insert a node "
                "with value X at the head of the linked list and return the head of the modified list."
            ),
            difficulty=Difficulty.EASY,
            input_format="Object format: {linkedList: array, X: integer}",
            output_format="Array representation after inserting X at the head",
            constraints="0 <= list length <= 10^5, -10^9 <= node values, X <= 10^9",
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
        logger.info(f"Seeded: {TITLE} with {len(test_cases)} test cases")


if __name__ == "__main__":
    asyncio.run(seed())