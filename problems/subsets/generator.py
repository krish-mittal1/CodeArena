from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> list[list[int]]:
    res = [[]]
    for x in nums:
        res += [subset + [x] for subset in res]
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 8)
        nums = rng.sample(range(-10, 11), n)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
