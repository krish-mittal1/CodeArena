from __future__ import annotations
import json
import random

def solve(obstacleGrid: list[list[int]]) -> int:
    m, n = len(obstacleGrid), len(obstacleGrid[0])
    if obstacleGrid[0][0] == 1 or obstacleGrid[m-1][n-1] == 1:
        return 0
    dp = [0] * n
    dp[0] = 1
    for i in range(m):
        for j in range(n):
            if obstacleGrid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        grid = [[1 if rng.random() < 0.15 else 0 for _ in range(n)] for _ in range(m)]
        grid[0][0] = 0
        grid[m-1][n-1] = 0
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve(grid)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
