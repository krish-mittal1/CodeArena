"""Bulk hidden test cases for Maximum Subarray."""

from __future__ import annotations

import json
import random


def solve(nums: list[int]) -> int:
    best = nums[0]
    current = nums[0]
    for value in nums[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best


FIXED = [
    [-1],
    [-5, -2, -9],
    [0, 0, 0],
    [1, 2, 3, 4],
    [-2, -1],
    [8, -19, 5, -4, 20],
    [100, -1, -2, -3, 50],
    [-10, 4, -1, 2, 1, -5, 4],
]


def generate_cases(*, count: int, seed: int, start_index: int):
    idx = start_index
    for nums in FIXED:
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1

    rng = random.Random(seed)
    generated = 0
    while generated < count:
        n = rng.randint(1, 420)
        nums = [rng.randint(-10**4, 10**4) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1
        generated += 1
