import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Longest Palindromic Substring"
TARGET_CASES = 581


def solve(s: str) -> str:
    best = ""
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                if right - left + 1 > len(best):
                    best = s[left:right + 1]
                left -= 1
                right += 1
    return best


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abccbaxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["babad", "cbbd", "a"]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["", "aaaa", "abcde", "racecar", "forgeeksskeegfor", "abacdfgdcaba", "anana", "abb"]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402031)
    while len(cases) < TARGET_CASES:
        s = rand_word(rng, rng.randint(0, 60))
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
                description="Given a string s, return the longest palindromic substring in s.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s",
                output_format="Longest palindromic substring",
                constraints="0 <= s.length <= 1000\ns consist of only digits and English letters.",
                method_name="longestPalindrome",
                parameters=[{"name": "s", "type": "string"}],
                return_type="string",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1300,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
