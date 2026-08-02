from __future__ import annotations
import json
import random

def solve(triangle: list[list[int]]) -> int:
    dp = triangle[-1][:]
    for r in range(len(triangle) - 2, -1, -1):
        for c in range(len(triangle[r])):
            dp[c] = triangle[r][c] + min(dp[c], dp[c + 1])
    return dp[0]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        rows = rng.randint(1, 10)
        triangle = [[rng.randint(-20, 20) for _ in range(r + 1)] for r in range(rows)]
        yield {
            "input": json.dumps(triangle),
            "expected_output": json.dumps(solve(triangle)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
