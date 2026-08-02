from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> int:
    x = 0
    for v in nums:
        x ^= v
    return x


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(0, 15)
        pairs = rng.sample(range(-50, 51), k + 1)
        single = pairs[0]
        nums = []
        for p in pairs[1:]:
            nums.extend([p, p])
        nums.append(single)
        rng.shuffle(nums)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
