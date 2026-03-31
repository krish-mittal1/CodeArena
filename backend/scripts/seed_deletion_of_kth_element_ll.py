"""
Seed script — insert/update 'Deletion of the Kth element of LL'
with 200+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_deletion_of_kth_element_ll
"""

import asyncio
import json
import logging
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Deletion of the Kth element of LL"


def delete_kth(values: list[int], k: int) -> list[int]:
    """Reference solver using array form of linked-list values."""
    if not values or k < 1 or k > len(values):
        return values
    return values[:k-1] + values[k:]


def make_case(values: list[int], k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps({"linkedList": values, "k": k}),
        "expected_output": json.dumps(delete_kth(values, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt-style samples.
    samples = [
        ([3, 4, 5], 2),
        ([1, 2, 3], 1),
        ([7, 7, 7], 3),
    ]
    for arr, k in samples:
        cases.append(make_case(arr, k, idx, is_sample=True))
        idx += 1

    # Edge cases.
    edge_cases = [
        ([1], 1),
        ([1, 2], 1),
        ([1, 2], 2),
        ([5, 5], 1),
        ([5, 5], 2),
        ([-1], 1),
        ([0], 1),
        ([1, 2, 3, 4, 5], 1),
        ([1, 2, 3, 4, 5], 5),
        ([1, 2, 3, 4, 5], 3),
        ([-5, -4, -3, -2, -1], 1),
        ([-5, -4, -3, -2, -1], 5),
        ([10, 20, 30, 40, 50], 3),
        ([1, 1, 1, 1, 1], 2),
        ([1, -1, 2, -2, 3], 3),
    ]
    for arr, k in edge_cases:
        cases.append(make_case(arr, k, idx))
        idx += 1

    # Structured deterministic cases.
    for n in [2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]:
        for k_pos in [1, n//2, n]:
            if k_pos <= n:
                inc = list(range(n))
                dec = list(range(n, 0, -1))
                alt = [i if i % 2 == 0 else -i for i in range(n)]
                const = [42] * n
                zigzag = [1, -1] * (n // 2) + ([1] if n % 2 else [])
                
                for arr in [inc, dec, alt, const, zigzag]:
                    cases.append(make_case(arr, k_pos, idx))
                    idx += 1

    # Deterministic randomized set to exceed 200.
    rng = random.Random(20260331)
    while len(cases) < 220:
        n = rng.randint(1, 3500)
        k = rng.randint(1, n)
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
            # Alternating pattern
            a, b = rng.randint(-100, 100), rng.randint(-100, 100)
            arr = [a if i % 2 == 0 else b for i in range(n)]

        cases.append(make_case(arr, k, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given the head of a singly linked list and an integer k, delete the kth node "
            "of the linked list and return the head of the modified list."
        )
        input_format = (
            "JSON object: {linkedList: [...], k: int}. "
            "The runner converts linkedList into head: ListNode and passes k as int."
        )
        output_format = "JSON array representing the list after deleting kth node"
        constraints = "1 <= k <= number of nodes <= 10^5\n-10^9 <= Node.val <= 10^9"

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.EASY
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "deleteKthNode"
            problem.parameters = [
                {"name": "head", "type": "ListNode"},
                {"name": "k", "type": "int"},
            ]
            problem.return_type = "ListNode"
            problem.time_limit_ms = 1000
            problem.memory_limit_mb = 256
            problem.rating = 800
            problem.is_active = True

            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception:
                logger.warning(
                    "Could not delete old test cases (referenced by submissions). "
                    "Keeping existing ones and updating metadata only."
                )
                await db.rollback()
                await db.refresh(problem)
        else:
            logger.info("Creating new problem entry.")
            problem = Problem(
                title=TITLE,
                description=description,
                difficulty=Difficulty.EASY,
                input_format=input_format,
                output_format=output_format,
                constraints=constraints,
                method_name="deleteKthNode",
                parameters=[
                    {"name": "head", "type": "ListNode"},
                    {"name": "k", "type": "int"},
                ],
                return_type="ListNode",
                time_limit_ms=1000,
                memory_limit_mb=256,
                rating=800,
                is_active=True,
            )
            db.add(problem)
            await db.flush()
            test_cases_deleted = True

        if test_cases_deleted:
            test_cases = build_test_cases()
            for tc in test_cases:
                db.add(TestCase(problem_id=problem.id, **tc))
            await db.commit()
            logger.info("Seeded '%s' with %d test cases.", TITLE, len(test_cases))
        else:
            await db.commit()
            logger.info("Updated metadata for '%s'. Test cases kept from previous seeding.", TITLE)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
