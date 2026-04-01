import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Word Break"
TARGET_CASES = 578


def solve(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[-1]


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("leetcode", ["leet", "code"]), ("applepenapple", ["apple", "pen"]), ("catsandog", ["cats", "dog", "sand", "and", "cat"])]
    for s, word_dict in samples:
        cases.append(make_case(s, word_dict, expected_output=solve(s, word_dict), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ("", ["a"]),
        ("a", ["a"]),
        ("aaaaaaa", ["aaaa", "aaa"]),
        ("cars", ["car", "ca", "rs"]),
        ("aaaaab", ["a", "aa", "aaa", "aaaa"]),
        ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]),
        ("catsanddog", ["cats", "dog", "sand", "and", "cat"]),
        ("bb", ["a", "b", "bbb", "bbbb"]),
    ]
    for s, word_dict in fixed:
        cases.append(make_case(s, word_dict, expected_output=solve(s, word_dict), idx=idx))
        idx += 1

    rng = random.Random(20260402038)
    alphabet = "abcde"
    while len(cases) < TARGET_CASES:
        dict_size = rng.randint(1, 8)
        word_dict = []
        for _ in range(dict_size):
            word = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5)))
            if word not in word_dict:
                word_dict.append(word)
        if rng.random() < 0.7:
            parts = [rng.choice(word_dict) for _ in range(rng.randint(0, 8))]
            s = "".join(parts)
        else:
            s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 20)))
        cases.append(make_case(s, word_dict, expected_output=solve(s, word_dict), idx=idx))
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
                description="Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.\n\nThe same word in the dictionary may be reused multiple times.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s\nLine 2: JSON array wordDict",
                output_format="Boolean true/false",
                constraints="0 <= s.length <= 300\n1 <= wordDict.length <= 1000\n1 <= wordDict[i].length <= 20\ns and wordDict[i] consist of lowercase English letters.",
                method_name="wordBreak",
                parameters=[{"name": "s", "type": "string"}, {"name": "wordDict", "type": "string[]"}],
                return_type="boolean",
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
