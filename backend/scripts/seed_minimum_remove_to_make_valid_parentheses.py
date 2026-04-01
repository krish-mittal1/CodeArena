import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Minimum Remove to Make Valid Parentheses"
TARGET_CASES = 563


def solve(s: str) -> str:
    stack = []
    remove = set()
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if stack:
                stack.pop()
            else:
                remove.add(i)
    remove.update(stack)
    return "".join(ch for i, ch in enumerate(s) if i not in remove)


def rand_string(rng: random.Random, length: int) -> str:
    alphabet = "abc()"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["lee(t(c)o)de)", "a)b(c)d", "))(("]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["", "abc", "((abc", "a((b)c)d)", "(()", "()())()", "(((())))", "))(a(b)c)d("]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402034)
    while len(cases) < TARGET_CASES:
        s = rand_string(rng, rng.randint(0, 80))
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
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
                description="Given a string s of '(', ')' and lowercase English characters, remove the minimum number of parentheses so that the resulting string is valid.\n\nReturn any valid string after the removals.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s",
                output_format="Valid string after minimum removals",
                constraints="0 <= s.length <= 10^5\ns[i] is either '(' , ')' , or lowercase English letter.",
                method_name="minRemoveToMakeValid",
                parameters=[{"name": "s", "type": "string"}],
                return_type="string",
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
