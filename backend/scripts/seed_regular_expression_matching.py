import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Regular Expression Matching"
TARGET_CASES = 573


def solve(s: str, p: str) -> bool:
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(2, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 2]
                if p[j - 2] in (".", s[i - 1]):
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            elif p[j - 1] in (".", s[i - 1]):
                dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]


def rand_string(rng: random.Random, length: int) -> str:
    alphabet = "abc"
    return "".join(rng.choice(alphabet) for _ in range(length))


def rand_pattern(rng: random.Random, length: int) -> str:
    alphabet = "abc."
    out = []
    for _ in range(length):
        ch = rng.choice(alphabet)
        out.append(ch)
        if rng.random() < 0.35:
            out.append("*")
    return "".join(out) or "a*"


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("aa", "a"), ("aa", "a*"), ("ab", ".*")]
    for s, p in samples:
        cases.append(make_case(s, p, expected_output=solve(s, p), idx=idx, is_sample=True))
        idx += 1

    fixed = [("", ""), ("", "a*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*."), ("aaa", "ab*a*c*a"), ("ab", ".*c"), ("aaa", "a*a"), ("bbbba", ".*a*a")]
    for s, p in fixed:
        cases.append(make_case(s, p, expected_output=solve(s, p), idx=idx))
        idx += 1

    rng = random.Random(20260402040)
    while len(cases) < TARGET_CASES:
        s = rand_string(rng, rng.randint(0, 14))
        p = rand_pattern(rng, rng.randint(0, 10))
        cases.append(make_case(s, p, expected_output=solve(s, p), idx=idx))
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
                description="Given an input string s and a pattern p, implement regular expression matching with support for '.' and '*'.\n\n'.' Matches any single character.\n'*' Matches zero or more of the preceding element.\n\nThe matching should cover the entire input string.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: string s\nLine 2: string p",
                output_format="Boolean true/false",
                constraints="0 <= s.length <= 20\n0 <= p.length <= 30\ns contains only lowercase English letters.\np contains only lowercase English letters, '.', and '*'.",
                method_name="isMatch",
                parameters=[{"name": "s", "type": "string"}, {"name": "p", "type": "string"}],
                return_type="boolean",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1650,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
