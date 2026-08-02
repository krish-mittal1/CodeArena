from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> int:
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            best = max(best, y - x)
    return best


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(0, 60)
        nums = [rng.randint(-50, 50) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
