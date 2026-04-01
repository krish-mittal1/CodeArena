import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Integer to Roman"
TARGET_CASES = 503


def solve(num: int) -> str:
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
    for num in [3, 58, 1994]:
        cases.append(make_case(num, expected_output=solve(num), idx=idx, is_sample=True))
        idx += 1

    fixed_nums = [1, 4, 9, 40, 90, 400, 944, 3999]
    for num in fixed_nums:
        cases.append(make_case(num, expected_output=solve(num), idx=idx))
        idx += 1

    rng = random.Random(20260402025)
    while len(cases) < TARGET_CASES:
        num = rng.randint(1, 3999)
        cases.append(make_case(num, expected_output=solve(num), idx=idx))
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
                description="Convert an integer to a Roman numeral.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: integer num",
                output_format="String Roman numeral",
                constraints="1 <= num <= 3999",
                method_name="intToRoman",
                parameters=[{"name": "num", "type": "int"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1050,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
