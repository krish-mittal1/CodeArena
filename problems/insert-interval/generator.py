from __future__ import annotations
import json
import random

def solve(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    res = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < newInterval[0]:
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    res.append(newInterval)
    while i < n:
        res.append(intervals[i])
        i += 1
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(0, 12)
        cur = 0
        intervals = []
        for _ in range(k):
            cur += rng.randint(0, 3)
            end = cur + rng.randint(0, 4)
            intervals.append([cur, end])
            cur = end + rng.randint(1, 3)
        a = rng.randint(0, 40)
        b = a + rng.randint(0, 8)
        yield {
            "input": f"{json.dumps(intervals)}\n{json.dumps([a, b])}",
            "expected_output": json.dumps(solve([x[:] for x in intervals], [a, b])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
