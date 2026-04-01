import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Multiply Strings"
TARGET_CASES = 531


def solve(num1: str, num2: str) -> str:
    return str(int(num1) * int(num2))


def rand_num(rng: random.Random, length: int) -> str:
    if length == 1:
        return str(rng.randint(0, 9))
    return str(rng.randint(1, 9)) + "".join(str(rng.randint(0, 9)) for _ in range(length - 1))


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [("2", "3"), ("123", "456"), ("0", "52")]
    for num1, num2 in samples:
        cases.append(make_case(num1, num2, expected_output=solve(num1, num2), idx=idx, is_sample=True))
        idx += 1

    fixed = [("0", "0"), ("1", "999"), ("999", "999"), ("500", "20"), ("1000", "1000"), ("123456789", "9"), ("10", "10"), ("99", "0")]
    for num1, num2 in fixed:
        cases.append(make_case(num1, num2, expected_output=solve(num1, num2), idx=idx))
        idx += 1

    rng = random.Random(20260402033)
    while len(cases) < TARGET_CASES:
        num1 = rand_num(rng, rng.randint(1, 18))
        num2 = rand_num(rng, rng.randint(1, 18))
        if rng.random() < 0.1:
            num1 = "0"
        if rng.random() < 0.1:
            num2 = "0"
        cases.append(make_case(num1, num2, expected_output=solve(num1, num2), idx=idx))
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
                description="Given two non-negative integers num1 and num2 represented as strings, return the product of num1 and num2, also represented as a string.\n\nYou must not use any built-in BigInteger library or convert the inputs directly to integers.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string num1\nLine 2: string num2",
                output_format="String product",
                constraints="1 <= num1.length, num2.length <= 200\nnum1 and num2 consist of digits only.\nBoth do not contain leading zeroes except the number 0 itself.",
                method_name="multiply",
                parameters=[{"name": "num1", "type": "string"}, {"name": "num2", "type": "string"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1250,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
