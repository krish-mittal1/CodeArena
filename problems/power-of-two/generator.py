from __future__ import annotations
import json
import random

def solve(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        if rng.random() < 0.4:
            n = 1 << rng.randint(0, 30)
        else:
            n = rng.randint(-100, 10**6)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
