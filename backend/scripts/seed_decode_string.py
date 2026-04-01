import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Decode String"
TARGET_CASES = 547


def solve(s: str) -> str:
    stack = []
    current = ""
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((current, num))
            current = ""
            num = 0
        elif ch == "]":
            prev, repeat = stack.pop()
            current = prev + current * repeat
        else:
            current += ch
    return current


def rand_encoded(rng: random.Random, depth: int = 0) -> str:
    alphabet = "abc"
    if depth >= 2 or rng.random() < 0.45:
        return "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5)))
    parts = []
    for _ in range(rng.randint(1, 3)):
        if rng.random() < 0.5:
            parts.append("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4))))
        else:
            parts.append(f"{rng.randint(1,4)}[{rand_encoded(rng, depth + 1)}]")
    return "".join(parts)


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef"]
    for s in samples:
        cases.append(make_case(s, expected_output=solve(s), idx=idx, is_sample=True))
        idx += 1

    fixed = ["10[a]", "2[ab3[c]]", "abc", "3[z]2[2[y]pq4[2[jk]e1[f]]]ef", "1[a]", "2[]", "2[a]3[b2[c]]", "12[ab]"]
    for s in fixed:
        cases.append(make_case(s, expected_output=solve(s), idx=idx))
        idx += 1

    rng = random.Random(20260402030)
    while len(cases) < TARGET_CASES:
        s = rand_encoded(rng)
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
                description="Given an encoded string, return its decoded string.\n\nThe encoding rule is: k[encoded_string], where the encoded_string inside the square brackets is repeated exactly k times. Assume the input string is always valid.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string s",
                output_format="Decoded string",
                constraints="1 <= s.length <= 300\ns consists of lowercase English letters, digits, and square brackets.\nAll integers in s are in the range [1, 300].",
                method_name="decodeString",
                parameters=[{"name": "s", "type": "string"}],
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
