from __future__ import annotations
import json
import random

def solve(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    def dfs(i, j):
        if i < 0 or j < 0 or i >= m or j >= n or grid[i][j] != 1:
            return 0
        grid[i][j] = 0
        return 1 + dfs(i+1,j) + dfs(i-1,j) + dfs(i,j+1) + dfs(i,j-1)
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                best = max(best, dfs(i, j))
    return best


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 10), rng.randint(1, 10)
        grid = [[1 if rng.random() < 0.35 else 0 for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve([row[:] for row in grid])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
