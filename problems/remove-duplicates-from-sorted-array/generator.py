from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> list[int]:
    if not nums:
        return []
    w = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[w - 1]:
            nums[w] = nums[i]
            w += 1
    return nums[:w]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = sorted(rng.randint(-20, 20) for _ in range(n))
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums[:])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
