from __future__ import annotations
import json
import random

def solve(n: int) -> int:
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def generate_cases(*, count: int, seed: int, start_index: int):
    for offset, n in enumerate(range(0, min(count, 31))):
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
