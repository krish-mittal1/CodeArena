import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Valid Number"
TARGET_CASES = 589


def solve(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    seen_digit = False
    seen_dot = False
    seen_exp = False
    digit_after_exp = True
    for i, ch in enumerate(s):
        if ch.isdigit():
            seen_digit = True
            if seen_exp:
                digit_after_exp = True
        elif ch in "+-":
            if i > 0 and s[i - 1].lower() != "e":
                return False
        elif ch == ".":
            if seen_dot or seen_exp:
                return False
            seen_dot = True
        elif ch.lower() == "e":
            if seen_exp or not seen_digit:
                return False
            seen_exp = True
            digit_after_exp = False
        else:
            return False
    return seen_digit and digit_after_exp


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["0", "e", "."]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["2", "0089", "-0.1", "+3.14", "4.", "-.9", "2e10", "-90E3", "3e+7", "+6e-1", "53.5e93", "-123.456e789", "abc", "1a", "1e", "e3", "99e2.5", "--6", "-+3", "95a54e53"]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402039)
    alphabet = "abcxyz"
    while len(cases) < TARGET_CASES:
        choice = rng.randint(0, 5)
        if choice == 0:
            s = str(rng.randint(-10**6, 10**6))
        elif choice == 1:
            s = f"{rng.choice(['', '+', '-'])}{rng.randint(0, 999)}.{rng.randint(0, 999)}"
        elif choice == 2:
            s = f"{rng.choice(['', '+', '-'])}{rng.randint(0, 999)}e{rng.choice(['', '+', '-'])}{rng.randint(0, 999)}"
        elif choice == 3:
            s = f"{rng.choice(['', '+', '-'])}.{rng.randint(0, 999)}"
        elif choice == 4:
            s = "".join(rng.choice(alphabet + "+-.eE0123456789") for _ in range(rng.randint(0, 12)))
        else:
            s = " " * rng.randint(0, 2) + str(rng.randint(-500, 500)) + " " * rng.randint(0, 2)
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
                description="A valid number can be split into these components in order: an optional sign, digits with an optional decimal point, and an optional exponent marked by 'e' or 'E'.\n\nGiven a string s, return true if s is a valid number.",
                difficulty=Difficulty.HARD,
                input_format="Line 1: string s",
                output_format="Boolean true/false",
                constraints="1 <= s.length <= 50\ns consists of English letters, digits, '+', '-', '.', and spaces.",
                method_name="isNumber",
                parameters=[{"name": "s", "type": "string"}],
                return_type="boolean",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=1550,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
