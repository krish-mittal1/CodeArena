import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Longest Common Prefix"
TARGET_CASES = 517


def solve(strs: list[str]) -> str:
    prefix = strs[0]
    for word in strs[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ["flower", "flow", "flight"],
        ["dog", "racecar", "car"],
        ["interspecies", "interstellar", "interstate"],
    ]
    for strs in samples:
        cases.append(make_case(strs, expected_output=solve(strs), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ["a"],
        ["", ""],
        ["ab", "a"],
        ["prefix", "prefix"],
        ["same", "same", "same"],
        ["aaab", "aaac", "aaad"],
        ["x", "y", "z"],
        ["throne", "throne", "throne-room"],
    ]
    for strs in fixed:
        cases.append(make_case(strs, expected_output=solve(strs), idx=idx))
        idx += 1

    rng = random.Random(20260402021)
    while len(cases) < TARGET_CASES:
        count = rng.randint(1, 10)
        base = rand_word(rng, rng.randint(0, 8))
        strs = []
        for _ in range(count):
            extra = rand_word(rng, rng.randint(0, 12))
            if rng.random() < 0.8:
                strs.append(base + extra)
            else:
                strs.append(rand_word(rng, rng.randint(0, 12)))
        cases.append(make_case(strs, expected_output=solve(strs), idx=idx))
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
                description="Write a function to find the longest common prefix string amongst an array of strings.\n\nIf there is no common prefix, return an empty string \"\".",
                difficulty=Difficulty.EASY,
                input_format="Line 1: JSON array strs",
                output_format="String: longest common prefix",
                constraints="1 <= strs.length <= 200\n0 <= strs[i].length <= 200\nstrs[i] consists of lowercase English letters.",
                method_name="longestCommonPrefix",
                parameters=[{"name": "strs", "type": "string[]"}],
                return_type="string",
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
