from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 30)
        nums = [rng.randint(-50, 50)]
        for _ in range(n - 1):
            nxt = rng.randint(-50, 50)
            while nxt == nums[-1]:
                nxt = rng.randint(-50, 50)
            nums.append(nxt)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
