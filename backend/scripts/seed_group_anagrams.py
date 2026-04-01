import asyncio
import random
from collections import defaultdict

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Group Anagrams"
TARGET_CASES = 523


def solve(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for word in strs:
        groups["".join(sorted(word))].append(word)
    return sorted([sorted(group) for group in groups.values()])


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcde"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ["eat", "tea", "tan", "ate", "nat", "bat"],
        [""],
        ["a"],
    ]
    for strs in samples:
        cases.append(make_case(strs, expected_output=solve(strs), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ["abc", "bca", "cab", "foo", "ofo"],
        ["", "", ""],
        ["ab", "ba", "cd", "dc", "ef"],
        ["zzz", "zzz", "zz"],
        ["listen", "silent", "enlist", "google"],
        ["a", "b", "c"],
        ["aa", "aa", "aa"],
        ["rat", "tar", "art", "star", "tars"],
    ]
    for strs in fixed:
        cases.append(make_case(strs, expected_output=solve(strs), idx=idx))
        idx += 1

    rng = random.Random(20260402029)
    while len(cases) < TARGET_CASES:
        count = rng.randint(1, 14)
        strs = []
        for _ in range(count):
            base = rand_word(rng, rng.randint(0, 8))
            if rng.random() < 0.4:
                chars = list(base)
                rng.shuffle(chars)
                strs.append("".join(chars))
            else:
                strs.append(base)
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
                description="Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON array strs",
                output_format="JSON array of string groups",
                constraints="1 <= strs.length <= 10^4\n0 <= strs[i].length <= 100\nstrs[i] consists of lowercase English letters.",
                method_name="groupAnagrams",
                parameters=[{"name": "strs", "type": "string[]"}],
                return_type="string[][]",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
