import asyncio
import json
import random
import string

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Valid Palindrome"


def solve(s: str) -> bool:
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]


def make_case(s: str, order_index: int, is_sample: bool = False) -> dict:
    return {
        "input": json.dumps(s),
        "expected_output": json.dumps(solve(s)),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for s in ["A man, a plan, a canal: Panama", "race a car"]:
        cases.append(make_case(s, idx, True)); idx += 1
    for s in ["", "a", "aa", "ab", ".,", "0P", "Madam", "No lemon, no melon", "Was it a car or a cat I saw?"]:
        cases.append(make_case(s, idx)); idx += 1
    rng = random.Random(20260331)
    alphabet = string.ascii_letters + string.digits + " ,.:;!?-_"
    while len(cases) < 170:
        n = rng.randint(0, 200)
        s = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(n))
        cases.append(make_case(s, idx)); idx += 1
    return cases


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(Problem).where(Problem.title == TITLE))
        problem = result.scalar_one_or_none()
        kwargs = dict(
            description="Given a string, decide whether it is a palindrome after lowercasing and removing non-alphanumeric characters.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON string s",
            output_format="Boolean: true if palindrome after normalization",
            constraints="0 <= s.length <= 2 * 10^5",
            method_name="isPalindrome",
            parameters=[{"name": "s", "type": "str"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=700,
            is_active=True,
        )
        if problem:
            for k, v in kwargs.items():
                setattr(problem, k, v)
            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception:
                await db.rollback()
                await db.refresh(problem)
        else:
            problem = Problem(title=TITLE, **kwargs)
            db.add(problem)
            await db.flush()
            test_cases_deleted = True
        if test_cases_deleted:
            for tc in build_test_cases():
                db.add(TestCase(problem_id=problem.id, **tc))
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
