import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.string_seed_utils import make_case, upsert_problem

TITLE = "Simplify Path"
TARGET_CASES = 516


def solve(path: str) -> str:
    stack = []
    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)


def rand_path(rng: random.Random) -> str:
    parts = []
    alphabet = "abcxyz"
    for _ in range(rng.randint(0, 18)):
        choice = rng.randint(0, 4)
        if choice == 0:
            parts.append(".")
        elif choice == 1:
            parts.append("..")
        elif choice == 2:
            parts.append("")
        else:
            parts.append("".join(rng.choice(alphabet) for _ in range(rng.randint(1, 5))))
    return "/" + "/".join(parts)


def build_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = ["/home/", "/../", "/home//foo/"]
    for path in samples:
        cases.append(make_case(path, expected_output=solve(path), idx=idx, is_sample=True))
        idx += 1

    fixed = ["/a/./b/../../c/", "/", "/...", "/a//b////c/d//././/..", "/../../../../../a", "/a/../../b/../c//.//", "/.", "/..hidden"]
    for path in fixed:
        cases.append(make_case(path, expected_output=solve(path), idx=idx))
        idx += 1

    rng = random.Random(20260402036)
    while len(cases) < TARGET_CASES:
        path = rand_path(rng)
        cases.append(make_case(path, expected_output=solve(path), idx=idx))
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
                description="Given an absolute path for a Unix-style file system, simplify it.\n\nA period '.' refers to the current directory, a double period '..' goes up one directory, and multiple slashes are treated as a single slash.\n\nReturn the simplified canonical path.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: string path",
                output_format="Simplified canonical path",
                constraints="1 <= path.length <= 3000\npath consists of English letters, digits, '.', '/', and '_'.",
                method_name="simplifyPath",
                parameters=[{"name": "path", "type": "string"}],
                return_type="string",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1200,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
