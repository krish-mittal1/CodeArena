"""Bulk hidden test cases for Container With Most Water."""

from __future__ import annotations

import json
import random


def solve(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        best = max(best, min(height[left], height[right]) * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


FIXED = [
    [1, 2],
    [2, 1],
    [4, 3, 2, 1, 4],
    [1, 2, 1],
    [9, 8, 7, 6, 5],
]


def generate_cases(*, count: int, seed: int, start_index: int):
    idx = start_index
    for height in FIXED:
        yield {
            "input": json.dumps(height),
            "expected_output": json.dumps(solve(height)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1

    rng = random.Random(seed)
    generated = 0
    while generated < count:
        n = rng.randint(2, 300)
        height = [rng.randint(0, 10**4) for _ in range(n)]
        yield {
            "input": json.dumps(height),
            "expected_output": json.dumps(solve(height)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1
        generated += 1
