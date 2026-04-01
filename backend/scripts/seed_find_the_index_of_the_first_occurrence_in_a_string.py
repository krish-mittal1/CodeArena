import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Find the Index of the First Occurrence in a String"
TARGET_CASES = 544


def solve(haystack: str, needle: str) -> int:
    return haystack.find(needle)


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcde"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("sadbutsad", "sad"), ("leetcode", "leeto"), ("aaaaa", "bba")]
    for haystack, needle in samples:
        cases.append(make_case(haystack, needle, expected_output=solve(haystack, needle), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ("a", "a"),
        ("aaa", "aa"),
        ("mississippi", "issi"),
        ("abc", "abcd"),
        ("needle", "needle"),
        ("abababab", "baba"),
        ("", ""),
        ("", "a"),
    ]
    for haystack, needle in fixed:
        cases.append(make_case(haystack, needle, expected_output=solve(haystack, needle), idx=idx))
        idx += 1

    rng = random.Random(20260402026)
    while len(cases) < TARGET_CASES:
        haystack = rand_word(rng, rng.randint(0, 80))
        if rng.random() < 0.7 and haystack:
            start = rng.randint(0, len(haystack))
            end = rng.randint(start, len(haystack))
            needle = haystack[start:end]
        else:
            needle = rand_word(rng, rng.randint(0, 12))
        cases.append(make_case(haystack, needle, expected_output=solve(haystack, needle), idx=idx))
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
                description="Given two strings needle and haystack, return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: string haystack\nLine 2: string needle",
                output_format="Single integer index or -1",
                constraints="0 <= haystack.length, needle.length <= 10^4\nhaystack and needle consist of lowercase English characters.",
                method_name="strStr",
                parameters=[{"name": "haystack", "type": "string"}, {"name": "needle", "type": "string"}],
                return_type="int",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=900,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
