from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> bool:
    s = sum(nums)
    if s % 2:
        return False
    target = s // 2
    dp = 1
    for x in nums:
        dp |= dp << x
    return bool(dp & (1 << target))


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 20)
        nums = [rng.randint(1, 30) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
