import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Count and Say"
TARGET_CASES = 501


def solve(n: int) -> str:
    s = "1"
    for _ in range(n - 1):
        out = []
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            out.append(str(j - i))
            out.append(s[i])
            i = j
        s = "".join(out)
    return s


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for n in [1, 4, 6]:
        cases.append(make_case(n, expected_output=solve(n), idx=idx, is_sample=True))
        idx += 1

    for n in [2, 3, 5, 7, 8, 10, 12, 15]:
        cases.append(make_case(n, expected_output=solve(n), idx=idx))
        idx += 1

    rng = random.Random(20260402037)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 20)
        cases.append(make_case(n, expected_output=solve(n), idx=idx))
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
                description="The count-and-say sequence is a sequence of digit strings defined by reading off the digits of the previous term.\n\nGiven an integer n, return the nth term of the count-and-say sequence.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: integer n",
                output_format="String nth term",
                constraints="1 <= n <= 30",
                method_name="countAndSay",
                parameters=[{"name": "n", "type": "int"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1100,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
