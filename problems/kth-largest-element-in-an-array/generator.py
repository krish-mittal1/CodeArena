from __future__ import annotations
import json
import random
import heapq

def solve(nums: list[int], k: int) -> int:
    return heapq.nlargest(k, nums)[-1]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 50)
        nums = [rng.randint(-100, 100) for _ in range(n)]
        k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(nums)}\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
