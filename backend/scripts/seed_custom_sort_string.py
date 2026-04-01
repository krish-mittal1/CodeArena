import asyncio
import random
from collections import Counter

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Custom Sort String"
TARGET_CASES = 521


def solve(order: str, s: str) -> str:
    count = Counter(s)
    out = []
    for ch in order:
        out.append(ch * count.pop(ch, 0))
    for ch, freq in sorted(count.items()):
        out.append(ch * freq)
    return "".join(out)


def rand_unique(rng: random.Random, length: int) -> str:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    rng.shuffle(alphabet)
    return "".join(alphabet[:length])


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("cba", "abcd"), ("bcafg", "abcd"), ("kqep", "pekeq")]
    for order, s in samples:
        cases.append(make_case(order, s, expected_output=solve(order, s), idx=idx, is_sample=True))
        idx += 1

    fixed = [("", "abc"), ("abc", ""), ("zyx", "xxyz"), ("a", "aaaa"), ("cba", "ccbbbaaadd"), ("qwerty", "typewriter"), ("abc", "def"), ("abcdef", "fedcba")]
    for order, s in fixed:
        cases.append(make_case(order, s, expected_output=solve(order, s), idx=idx))
        idx += 1

    rng = random.Random(20260402035)
    while len(cases) < TARGET_CASES:
        order = rand_unique(rng, rng.randint(0, 12))
        s = rand_word(rng, rng.randint(0, 70))
        cases.append(make_case(order, s, expected_output=solve(order, s), idx=idx))
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
                description="You are given two strings order and s. All the characters of order are unique and were sorted in some custom order previously.\n\nPermute the characters of s so that they match the order given by order as much as possible. Return any such permutation.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string order\nLine 2: string s",
                output_format="Reordered string",
                constraints="0 <= order.length <= 26\n0 <= s.length <= 200\norder and s consist of lowercase English letters.",
                method_name="customSortString",
                parameters=[{"name": "order", "type": "string"}, {"name": "s", "type": "string"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1150,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
