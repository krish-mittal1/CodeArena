from __future__ import annotations
import json
import random

def solve(board: list[list[str]], word: str) -> bool:
    if not board or not board[0]:
        return False
    m, n = len(board), len(board[0])
    grid = [row[:] for row in board]

    def dfs(r, c, k):
        if k == len(word):
            return True
        if r < 0 or c < 0 or r >= m or c >= n or grid[r][c] != word[k]:
            return False
        tmp = grid[r][c]
        grid[r][c] = "#"
        ok = dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1) or dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1)
        grid[r][c] = tmp
        return ok

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "ABCDE"
    edges = [
        ([["A"]], "A"),
        ([["A"]], "B"),
        ([["A", "B"], ["C", "D"]], "ABDC"),
        ([["A", "B"], ["C", "D"]], "ABAB"),
        ([["A", "A", "A"], ["A", "A", "A"]], "AAAA"),
    ]
    for offset in range(count):
        if offset < len(edges):
            board, word = edges[offset]
        else:
            m, n = rng.randint(1, 4), rng.randint(1, 4)
            board = [[rng.choice(letters) for _ in range(n)] for _ in range(m)]
            if rng.random() < 0.5:
                word = "".join(board[0][: min(n, 3)])
            else:
                word = "".join(rng.choice(letters) for _ in range(rng.randint(1, 5)))
        yield {
            "input": f"{json.dumps(board)}\n{json.dumps(word)}",
            "expected_output": json.dumps(solve(board, word)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
