import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TITLE = "Game of Life"
TARGET_CASES = 524


def solve(board: list[list[int]]) -> list[list[int]]:
    rows = len(board)
    cols = len(board[0]) if rows else 0
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            live = 0
            for nr in range(max(0, r - 1), min(rows, r + 2)):
                for nc in range(max(0, c - 1), min(cols, c + 2)):
                    if nr == r and nc == c:
                        continue
                    live += board[nr][nc]
            if board[r][c] == 1:
                out[r][c] = 1 if live in (2, 3) else 0
            else:
                out[r][c] = 1 if live == 3 else 0
    return out


def build_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0

    for board in (
        [[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[1, 1], [1, 0]],
        [[1]],
    ):
        cases.append(make_case(board, expected_output=solve(board), idx=idx, is_sample=True))
        idx += 1

    fixed = [
        [[0]],
        [[1, 1, 1]],
        [[1], [1], [1]],
        [[1, 1], [1, 1]],
        [[0, 0, 0], [0, 0, 0]],
        [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
        [[1, 1, 0], [1, 0, 0], [0, 0, 1]],
        [[0, 1, 0, 1], [1, 1, 1, 0]],
    ]
    for board in fixed:
        cases.append(make_case(board, expected_output=solve(board), idx=idx))
        idx += 1

    rng = random.Random(2026040212)
    while len(cases) < TARGET_CASES:
        rows = rng.randint(1, 20)
        cols = rng.randint(1, 20)
        board = [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
        cases.append(make_case(board, expected_output=solve(board), idx=idx))
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
                description="According to Wikipedia's article: \"The Game of Life, also known simply as Life, is a cellular automaton devised by the British mathematician John Horton Conway.\"\n\nGiven the current state of the m x n grid board, return the next state after applying the classic Game of Life rules.",
                difficulty=Difficulty.MEDIUM,
                input_format="Line 1: JSON 2D array board",
                output_format="JSON 2D array representing the next board state",
                constraints="1 <= board.length, board[0].length <= 20\nboard[i][j] is 0 or 1",
                method_name="gameOfLife",
                parameters=[{"name": "board", "type": "int[][]"}],
                return_type="int[][]",
                time_limit_ms=1500,
                memory_limit_mb=256,
                rating=1300,
                is_active=True,
            ),
            build_cases(),
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
