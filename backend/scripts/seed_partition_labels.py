import asyncio
import json
import random

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

TITLE = "Partition Labels"


def solve(s: str) -> list[int]:
    last = {ch: i for i, ch in enumerate(s)}
    start = end = 0
    parts = []
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            parts.append(end - start + 1)
            start = i + 1
    return parts


def make_case(s: str, idx: int, is_sample: bool = False) -> dict:
    return {"input": json.dumps(s), "expected_output": json.dumps(solve(s)), "order_index": idx, "is_sample": is_sample}


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for s in ["ababcbacadefegdehijhklij", "eccbbbbdec"]:
        cases.append(make_case(s, idx, True)); idx += 1
    for s in ["a", "ab", "aa", "abcabc", "abc", "zzxyzz", "abcddcba", "qiejxqfnqceocmy"]:
        cases.append(make_case(s, idx)); idx += 1
    rng = random.Random(20260331)
    alphabet = "abcdefghi"
    while len(cases) < 180:
        n = rng.randint(1, 180)
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
            description="Partition a string into as many parts as possible so that each letter appears in at most one part. Return the sizes of the parts in order.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON string s",
            output_format="JSON array of integers: partition sizes",
            constraints="1 <= s.length <= 500",
            method_name="partitionLabels",
            parameters=[{"name": "s", "type": "str"}],
            return_type="int[]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1100,
            is_active=True,
        )
        if problem:
            for k, v in kwargs.items():
                setattr(problem, k, v)
            deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id)); await db.flush(); deleted = True
            except Exception:
                await db.rollback(); await db.refresh(problem)
        else:
            problem = Problem(title=TITLE, **kwargs)
            db.add(problem); await db.flush(); deleted = True
        if deleted:
            for tc in build_cases():
                db.add(TestCase(problem_id=problem.id, **tc))
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
