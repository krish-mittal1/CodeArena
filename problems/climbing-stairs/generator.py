from __future__ import annotations
import json
import random

def solve(n: int) -> int:
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 45)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
