import asyncio
import random
import string

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TITLE = "Way Too Long Words"
TARGET_CASES = 538


def shorten(word: str) -> str:
    if len(word) <= 10:
        return word
    return f"{word[0]}{len(word) - 2}{word[-1]}"


def solve(words: list[str]) -> str:
    return "\n".join(shorten(word) for word in words)


def make_input(words: list[str]) -> str:
    return "\n".join([str(len(words)), *words])


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    samples = [
        ["word", "localization", "internationalization", "pneumonoultramicroscopicsilicovolcanoconiosis"],
        ["short", "abcdefghij", "abcdefghijk"],
        ["a", "banana", "codeforces"],
    ]
    for words in samples:
        cases.append(make_case(make_input(words), solve(words), idx, is_sample=True))
        idx += 1

    fixed = [
        ["x"],
        ["z" * 10],
        ["abcdefghijklmno"],
        ["a" * 11],
        ["b" * 12],
        ["hi", "helloworld", "helloworlds"],
        ["a" * 100],
        ["b" * 119, "c" * 120],
        ["edgecase", "tiny", "massivelylongwordtest"],
        ["programming", "contest", "rating", "ladder"],
        ["short", "small", "mini", "micro", "supercalifragilistic"],
        ["a", "ab", "abc", "abcd", "abcde", "abcdef", "abcdefg", "abcdefgh", "abcdefghi", "abcdefghij", "abcdefghijk"],
        ["localization", "internationalization", "accessibility", "automatically"],
        ["qwertyuiopasdfghjkl", "bbbbbbbbbbb", "cccccccccccccccccccc"],
        ["single", "word"],
    ]
    for words in fixed:
        cases.append(make_case(make_input(words), solve(words), idx))
        idx += 1

    rng = random.Random(2026040203)
    alphabet = string.ascii_lowercase
    while len(cases) < TARGET_CASES:
        count = rng.randint(1, 25)
        words = []
        for _ in range(count):
            length = rng.randint(1, 120)
            words.append("".join(rng.choice(alphabet) for _ in range(length)))
        cases.append(make_case(make_input(words), solve(words), idx))
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
                description=(
                    "For each given word, print it unchanged if its length is at most 10. "
                    "Otherwise print the first letter, then the number of omitted middle letters, "
                    "then the last letter."
                ),
                difficulty=Difficulty.EASY,
                input_format="Line 1: integer n\nNext n lines: one lowercase word each",
                output_format="Print n lines, one transformed word per line.",
                constraints="1 <= n <= 25\n1 <= word length <= 120",
                problem_type="cp",
                time_limit_ms=1000,
                memory_limit_mb=256,
                rating=800,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
