from __future__ import annotations
import json
import math
import random

def solve(m: int, n: int) -> int:
    return math.comb(m + n - 2, m - 1)

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m = rng.randint(1, 25)
        n = rng.randint(1, 25)
        yield {
            "input": f"{json.dumps(m)}\n{json.dumps(n)}",
            "expected_output": json.dumps(solve(m, n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
