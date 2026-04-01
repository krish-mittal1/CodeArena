import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Zigzag Conversion"
TARGET_CASES = 552


def solve(s: str, num_rows: int) -> str:
    if num_rows == 1 or num_rows >= len(s):
        return s
    rows = [""] * num_rows
    row = 0
    step = 1
    for ch in s:
        rows[row] += ch
        if row == 0:
            step = 1
        elif row == num_rows - 1:
            step = -1
        row += step
    return "".join(rows)


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("PAYPALISHIRING", 3), ("PAYPALISHIRING", 4), ("A", 1)]
    for s, num_rows in samples:
        cases.append(make_case(s, num_rows, expected_output=solve(s, num_rows), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ("AB", 1),
        ("AB", 2),
        ("ABCDE", 4),
        ("HELLOWORLD", 2),
        ("HELLOWORLD", 20),
        ("", 5),
        ("SINGLE", 1),
        ("ZIGZAG", 3),
    ]
    for s, num_rows in fixed:
        cases.append(make_case(s, num_rows, expected_output=solve(s, num_rows), idx=idx))
        idx += 1

    rng = random.Random(20260402027)
    while len(cases) < TARGET_CASES:
        s = rand_word(rng, rng.randint(0, 120))
        num_rows = rng.randint(1, 15)
        cases.append(make_case(s, num_rows, expected_output=solve(s, num_rows), idx=idx))
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
                description="The string \"PAYPALISHIRING\" is written in a zigzag pattern on a given number of rows. Read line by line to produce a new string.\n\nGiven a string s and an integer numRows, return the converted string.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s\nLine 2: integer numRows",
                output_format="Converted zigzag string",
                constraints="0 <= s.length <= 1000\n1 <= numRows <= 1000\ns consists of English letters, ',' and '.'.",
                method_name="convert",
                parameters=[{"name": "s", "type": "string"}, {"name": "numRows", "type": "int"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1100,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
