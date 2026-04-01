import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "String to Integer (atoi)"
TARGET_CASES = 567


def solve(s: str) -> int:
    i = 0
    n = len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1
    num = 0
    while i < n and s[i].isdigit():
        num = num * 10 + int(s[i])
        i += 1
    num *= sign
    return max(-(2**31), min(2**31 - 1, num))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["42", "   -42", "4193 with words"]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["words and 987", "-91283472332", "+1", "00000-42a1234", "   +0 123", "", "2147483648", "-2147483649"]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402028)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    while len(cases) < TARGET_CASES:
        choice = rng.randint(0, 4)
        if choice == 0:
            s = " " * rng.randint(0, 4) + rng.choice(["+", "-", ""]) + str(rng.randint(-10**12, 10**12))
        elif choice == 1:
            s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
        elif choice == 2:
            s = " " * rng.randint(0, 3) + rng.choice(["+", "-", ""]) + "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(0, 18))) + rng.choice(["", "abc"])
        elif choice == 3:
            s = rng.choice(["+-12", "-+12", "  000123", "  -0012a42"])
        else:
            s = ""
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
                description="Implement the myAtoi(string s) function, which converts a string to a 32-bit signed integer.\n\nThe algorithm should discard leading whitespace, take an optional sign, read in the next characters until a non-digit is found, and clamp the value to the 32-bit signed range.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s",
                output_format="Single integer result",
                constraints="0 <= s.length <= 200\ns consists of English letters, digits, spaces, '+', '-', and '.'.",
                method_name="myAtoi",
                parameters=[{"name": "s", "type": "string"}],
                return_type="int",
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
