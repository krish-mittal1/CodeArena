"""
Seed script — insert/update 'Deletion of the head of LL'
with 100+ test cases (samples + edge + deterministic stress cases).

Usage:
    python -m backend.scripts.seed_deletion_of_head_ll
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

TITLE = "Deletion of the head of LL"


def delete_head(values: list[int]) -> list[int]:
    """Reference solver using array form of linked-list values."""
    if not values:
        return []
    return values[1:]


def make_case(values: list[int], order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(values),
        "expected_output": json.dumps(delete_head(values)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # Prompt-style samples.
    samples = [
        [1, 2, 3],
        [1],
        [9, 8, 7, 6],
    ]
    for arr in samples:
        cases.append(make_case(arr, idx, is_sample=True))
        idx += 1

    # Edge cases.
    edge_cases = [
        [],
        [0],
        [-1],
        [10**9],
        [-10**9],
        [5, 5],
        [-5, -4, -3, -2, -1],
        [1, 2],
        [2, 1],
        [7, 7, 7, 7, 7],
    ]
    for arr in edge_cases:
        cases.append(make_case(arr, idx))
        idx += 1

    # Structured deterministic cases.
    for n in [3, 5, 10, 20, 50, 100, 200, 500, 1000]:
        inc = list(range(n))
        dec = list(range(n, 0, -1))
        alt = [i if i % 2 == 0 else -i for i in range(n)]
        const = [42] * n
        for arr in [inc, dec, alt, const]:
            cases.append(make_case(arr, idx))
            idx += 1

    # Deterministic randomized set to exceed 100.
    rng = random.Random(20260405)
    while len(cases) < 120:
        n = rng.randint(0, 2500)
        mode = rng.randint(0, 3)

        if mode == 0:
            arr = [rng.randint(-1000, 1000) for _ in range(n)]
        elif mode == 1:
            start = rng.randint(-50000, 50000)
            arr = [start + i for i in range(n)]
        elif mode == 2:
            arr = [rng.choice([-1, 0, 1, 2, 3, 5, 8]) for _ in range(n)]
        else:
            arr = [rng.randint(-10**9, 10**9) for _ in range(n)]

        cases.append(make_case(arr, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given the head of a singly linked list, delete the head node and "
            "return the head of the modified list.\n\n"
            "Example 1\n"
            "Input: head = [1, 2, 3]\n"
            "Output: [2, 3]\n\n"
            "Example 2\n"
            "Input: head = [1]\n"
            "Output: []\n\n"
            "Example 3\n"
            "Input: head = [9, 8, 7, 6]\n"
            "Output: [8, 7, 6]"
        )

        input_format = (
            "Line 1: JSON array representing linked-list node values in order. "
            "The runner converts this array into head: ListNode before calling your method."
        )
        output_format = (
            "JSON array representing the updated linked list after deleting the head node"
        )
        constraints = (
            "0 <= number of nodes <= 10^5\n"
            "-10^9 <= Node.val <= 10^9"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.EASY
            problem.input_format = input_format
            problem.output_format = output_format
            problem.constraints = constraints
            problem.method_name = "deleteHead"
            problem.parameters = [{"name": "head", "type": "ListNode"}]
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
                method_name="deleteHead",
                parameters=[{"name": "head", "type": "ListNode"}],
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
