"""Bulk hidden test cases for Merge Intervals."""

from __future__ import annotations

import json
import random


def solve(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    ordered = sorted((interval[:] for interval in intervals), key=lambda item: item[0])
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


FIXED = [
    [[1, 2]],
    [[1, 4], [5, 6]],
    [[5, 7], [1, 3], [2, 4]],
    [[1, 10], [2, 3], [4, 8]],
    [[-10, -1], [-5, 0], [1, 2]],
    [[1, 5], [2, 3], [4, 6], [7, 8]],
    [[0, 0], [0, 1], [2, 2]],
    [[1, 100], [20, 30], [31, 40], [90, 120]],
]


def generate_cases(*, count: int, seed: int, start_index: int):
    idx = start_index
    for intervals in FIXED:
        yield {
            "input": json.dumps(intervals),
            "expected_output": json.dumps(solve(intervals)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1

    rng = random.Random(seed)
    generated = 0
    while generated < count:
        n = rng.randint(1, 180)
        intervals: list[list[int]] = []
        base = rng.randint(-200, 200)
        for _ in range(n):
            start = base + rng.randint(-50, 120)
            end = start + rng.randint(0, 50)
            intervals.append([start, end])
        yield {
            "input": json.dumps(intervals),
            "expected_output": json.dumps(solve(intervals)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1
        generated += 1
