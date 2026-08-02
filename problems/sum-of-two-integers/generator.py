from __future__ import annotations
import json
import random

def solve(a: int, b: int) -> int:
    # Python ints are unbounded; mask to 32-bit two's complement behavior
    MASK = 0xFFFFFFFF
    MAX = 0x7FFFFFFF
    while b & MASK:
        carry = (a & b) << 1
        a = (a ^ b) & MASK
        b = carry & MASK
    return a if a <= MAX else ~(a ^ MASK)


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        a, b = rng.randint(-1000, 1000), rng.randint(-1000, 1000)
        yield {
            "input": f"{json.dumps(a)}\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
