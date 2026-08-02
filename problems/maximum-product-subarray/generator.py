from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> int:
    max_p = min_p = ans = nums[0]
    for x in nums[1:]:
        candidates = (x, max_p * x, min_p * x)
        max_p, min_p = max(candidates), min(candidates)
        ans = max(ans, max_p)
    return ans


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
