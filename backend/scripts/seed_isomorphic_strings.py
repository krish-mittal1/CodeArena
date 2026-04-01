import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Isomorphic Strings"
TARGET_CASES = 533


def solve(s: str, t: str) -> bool:
    map_st = {}
    map_ts = {}
    for a, b in zip(s, t):
        if map_st.get(a, b) != b or map_ts.get(b, a) != a:
            return False
        map_st[a] = b
        map_ts[b] = a
    return True


def build_isomorphic_pair(rng: random.Random, length: int) -> tuple[str, str]:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    s = "".join(rng.choice(alphabet[:8]) for _ in range(length))
    mapping = {}
    available = list(alphabet)
    rng.shuffle(available)
    out = []
    for ch in s:
        if ch not in mapping:
            mapping[ch] = available.pop()
        out.append(mapping[ch])
    return s, "".join(out)


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("egg", "add"), ("foo", "bar"), ("paper", "title")]
    for s, t in samples:
        cases.append(make_case(s, t, expected_output=solve(s, t), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ("badc", "baba"),
        ("a", "z"),
        ("ab", "ca"),
        ("aa", "ab"),
        ("abcabc", "xyzxyz"),
        ("abba", "cddc"),
        ("abba", "cddd"),
        ("", ""),
    ]
    for s, t in fixed:
        cases.append(make_case(s, t, expected_output=solve(s, t), idx=idx))
        idx += 1

    rng = random.Random(20260402023)
    while len(cases) < TARGET_CASES:
        length = rng.randint(0, 60)
        if rng.random() < 0.6:
            s, t = build_isomorphic_pair(rng, length)
        else:
            s, t = rand_word(rng, length), rand_word(rng, length)
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
                description="Given two strings s and t, determine if they are isomorphic.\n\nTwo strings are isomorphic if the characters in s can be replaced to get t while preserving order. No two characters may map to the same character, but a character may map to itself.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: string s\nLine 2: string t",
                output_format="Boolean true/false",
                constraints="0 <= s.length <= 5 * 10^4\ns.length == t.length\ns and t consist of valid ASCII characters.",
                method_name="isIsomorphic",
                parameters=[{"name": "s", "type": "string"}, {"name": "t", "type": "string"}],
                return_type="boolean",
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
