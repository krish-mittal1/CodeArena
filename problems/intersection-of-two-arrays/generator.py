from __future__ import annotations
import json
import random

def solve(nums1: list[int], nums2: list[int]) -> list[int]:
    return list(set(nums1) & set(nums2))


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        a = [rng.randint(0, 30) for _ in range(rng.randint(1, 20))]
        b = [rng.randint(0, 30) for _ in range(rng.randint(1, 20))]
        yield {
            "input": f"{json.dumps(a)}\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
