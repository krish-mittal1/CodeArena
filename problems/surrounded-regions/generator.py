from __future__ import annotations
import json
import random

def solve(board: list[str]) -> list[str]:
    if not board:
        return board
    m, n = len(board), len(board[0])
    g = [list(row) for row in board]
    def dfs(i, j):
        if i < 0 or j < 0 or i >= m or j >= n or g[i][j] != "O":
            return
        g[i][j] = "S"
        dfs(i+1,j); dfs(i-1,j); dfs(i,j+1); dfs(i,j-1)
    for i in range(m):
        dfs(i, 0); dfs(i, n-1)
    for j in range(n):
        dfs(0, j); dfs(m-1, j)
    for i in range(m):
        for j in range(n):
            if g[i][j] == "O":
                g[i][j] = "X"
            elif g[i][j] == "S":
                g[i][j] = "O"
    return ["".join(row) for row in g]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        board = ["".join(rng.choice("XO") for _ in range(n)) for _ in range(m)]
        yield {
            "input": json.dumps(board),
            "expected_output": json.dumps(solve(board)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
