"""
Seed script — insert/update 'Maximum Points You Can Obtain from Cards'
with 100+ test cases (samples + edge + randomized).

Usage:
    python -m backend.scripts.seed_max_points_cards
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

TITLE = "Maximum Points You Can Obtain from Cards"


def max_score(card_score: list[int], k: int) -> int:
    """Reference solver using sliding window on left/right pick split."""
    n = len(card_score)
    if k <= 0:
        return 0
    if k >= n:
        return sum(card_score)

    current = sum(card_score[:k])
    best = current
    right_idx = n - 1

    for left_take in range(k - 1, -1, -1):
        current -= card_score[left_take]
        current += card_score[right_idx]
        right_idx -= 1
        best = max(best, current)

    return best


def make_case(cards: list[int], k: int, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(cards) + "\n" + json.dumps(k),
        "expected_output": json.dumps(max_score(cards, k)),
        "is_sample": is_sample,
        "order_index": order_index,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    # ── Samples from prompt ─────────────────────────────────────────────
    cases.append(make_case([1, 2, 3, 4, 5, 6], 3, idx, is_sample=True)); idx += 1
    cases.append(make_case([5, 4, 1, 8, 7, 1, 3], 3, idx, is_sample=True)); idx += 1

    # ── Edge cases ──────────────────────────────────────────────────────
    edge_inputs = [
        ([10], 1),
        ([10], 0),
        ([2, 8], 1),
        ([2, 8], 2),
        ([0, 0, 0, 0], 2),
        ([-5, -2, -9, -1], 2),
        ([100, -100, 100, -100, 100], 3),
        ([9, 7, 7, 9, 7, 7, 9], 7),
        ([1, 1000, 1], 1),
        ([1, 1000, 1], 2),
        ([1, 1000, 1], 3),
        ([50, 1, 1, 1, 50], 2),
        ([50, 1, 1, 1, 50], 3),
        ([1, 2, 3, 4, 5], 0),
        ([1, 2, 3, 4, 5], 5),
    ]
    for cards, k in edge_inputs:
        cases.append(make_case(cards, k, idx)); idx += 1

    # Patterned arrays to stress left/right split boundaries.
    for n in [6, 8, 10, 16, 25, 40]:
        inc = list(range(1, n + 1))
        dec = list(range(n, 0, -1))
        alt = [100 if i % 2 == 0 else -100 for i in range(n)]
        for k in [1, 2, n // 2, max(0, n - 1), n]:
            cases.append(make_case(inc, k, idx)); idx += 1
            cases.append(make_case(dec, k, idx)); idx += 1
            cases.append(make_case(alt, k, idx)); idx += 1

    # ── Randomized set (deterministic seed) ─────────────────────────────
    random.seed(20260329)
    while len(cases) < 130:
        n = random.randint(1, 500)
        cards = [random.randint(-1000, 1000) for _ in range(n)]
        k = random.randint(0, n)
        cases.append(make_case(cards, k, idx))
        idx += 1

    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()

        description = (
            "Given N cards arranged in a row, each card has an associated score denoted by "
            "the cardScore array. Choose exactly k cards. In each step, a card can be chosen "
            "either from the beginning or the end of the row.\n\n"
            "Return the maximum score that can be obtained.\n\n"
            "Example 1\n"
            "Input : cardScore = [1, 2, 3, 4, 5, 6] , k = 3\n"
            "Output : 15\n\n"
            "Example 2\n"
            "Input : cardScore = [5, 4, 1, 8, 7, 1, 3 ] , k = 3\n"
            "Output : 12"
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.difficulty = Difficulty.MEDIUM
            problem.input_format = "Line 1: JSON array cardScore (int[])\\nLine 2: integer k"
            problem.output_format = "Single integer: maximum obtainable score"
            problem.constraints = "1 <= cardScore.length <= 10^5\\n-10^4 <= cardScore[i] <= 10^4\\n0 <= k <= cardScore.length"
            problem.method_name = "maxScore"
            problem.parameters = [
                {"name": "cardScore", "type": "int[]"},
                {"name": "k", "type": "int"},
            ]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 1200
            problem.is_active = True

            await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
            await db.flush()
        else:
            logger.info("Creating new problem entry.")
            problem = Problem(
                title=TITLE,
                description=description,
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array cardScore (int[])\\nLine 2: integer k",
                output_format="Single integer: maximum obtainable score",
                constraints="1 <= cardScore.length <= 10^5\\n-10^4 <= cardScore[i] <= 10^4\\n0 <= k <= cardScore.length",
                method_name="maxScore",
                parameters=[
                    {"name": "cardScore", "type": "int[]"},
                    {"name": "k", "type": "int"},
                ],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            )
            db.add(problem)
            await db.flush()

        test_cases = build_test_cases()
        for tc in test_cases:
            db.add(TestCase(problem_id=problem.id, **tc))

        await db.commit()
        logger.info("Seeded '%s' with %d test cases.", TITLE, len(test_cases))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
