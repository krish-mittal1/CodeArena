import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Valid Anagram"
TARGET_CASES = 538


def solve(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("anagram", "nagaram"), ("rat", "car"), ("", "")]
    for s, t in samples:
        cases.append(make_case(s, t, expected_output=solve(s, t), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ("a", "a"),
        ("ab", "ba"),
        ("ab", "aa"),
        ("listen", "silent"),
        ("triangle", "integral"),
        ("hello", "bello"),
        ("aaabbb", "bbbaaa"),
        ("zzz", "zzzz"),
    ]
    for s, t in fixed:
        cases.append(make_case(s, t, expected_output=solve(s, t), idx=idx))
        idx += 1

    rng = random.Random(20260402022)
    while len(cases) < TARGET_CASES:
        length = rng.randint(0, 60)
        s = rand_word(rng, length)
        if rng.random() < 0.65:
            chars = list(s)
            rng.shuffle(chars)
            t = "".join(chars)
        else:
            t = rand_word(rng, rng.randint(max(0, length - 2), length + 2))
        cases.append(make_case(s, t, expected_output=solve(s, t), idx=idx))
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
                description="Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: string s\nLine 2: string t",
                output_format="Boolean true/false",
                constraints="0 <= s.length, t.length <= 5 * 10^4\ns and t consist of lowercase English letters.",
                method_name="isAnagram",
                parameters=[{"name": "s", "type": "string"}, {"name": "t", "type": "string"}],
                return_type="boolean",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=850,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
