from __future__ import annotations
import json
import random

def solve(cost: list[int]) -> int:
    a = b = 0
    for c in reversed(cost):
        a, b = c + min(a, b), a
    return min(a, b)


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(2, 40)
        cost = [rng.randint(0, 100) for _ in range(n)]
        yield {
            "input": json.dumps(cost),
            "expected_output": json.dumps(solve(cost)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
