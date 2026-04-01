import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Palindromic Substrings"
TARGET_CASES = 559


def solve(s: str) -> int:
    total = 0
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1
                left -= 1
                right += 1
    return total


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abc"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["abc", "aaa", "abba"]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["", "a", "aaaa", "abccba", "abcdedcba", "xyz", "abababa", "abcddcbaef"]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402032)
    while len(cases) < TARGET_CASES:
        s = rand_word(rng, rng.randint(0, 70))
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
                description="Given a string s, return the number of palindromic substrings in it.\n\nA string is a palindrome when it reads the same backward as forward. A substring is a contiguous sequence of characters within the string.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s",
                output_format="Single integer count",
                constraints="0 <= s.length <= 1000\ns consists of lowercase English letters.",
                method_name="countSubstrings",
                parameters=[{"name": "s", "type": "string"}],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1250,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
