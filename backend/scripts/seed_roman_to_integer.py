import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Roman to Integer"
TARGET_CASES = 509


VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def solve(s: str) -> int:
    total = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and VALUES[ch] < VALUES[s[i + 1]]:
            total -= VALUES[ch]
        else:
            total += VALUES[ch]
    return total


def to_roman(num: int) -> str:
    values = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = []
    for value, token in values:
        while num >= value:
            result.append(token)
            num -= value
    return "".join(result)


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    for s in ["III", "LVIII", "MCMXCIV"]:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed_nums = [1, 4, 9, 40, 58, 90, 400, 944]
    for num in fixed_nums:
        s = to_roman(num)
        cases.append(make_case(s, expected_output=num, idx=idx))
        idx += 1

    rng = random.Random(20260402024)
    while len(cases) < TARGET_CASES:
        num = rng.randint(1, 3999)
        s = to_roman(num)
        cases.append(make_case(s, expected_output=num, idx=idx))
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
                description="Roman numerals are represented by seven different symbols: I, V, X, L, C, D and M.\n\nGiven a roman numeral, convert it to an integer.",
                difficulty=Difficulty.EASY,
                input_format="Line 1: string s",
                output_format="Single integer value",
                constraints="1 <= s.length <= 15\ns is a valid Roman numeral in the range [1, 3999].",
                method_name="romanToInt",
                parameters=[{"name": "s", "type": "string"}],
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
