from __future__ import annotations
import json
import random

def solve(nums: list[int], target: int) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        nums = sorted({rng.randint(1, 15) for _ in range(rng.randint(1, 6))})
        target = rng.randint(1, 40)
        yield {
            "input": f"{json.dumps(nums)}\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(nums, target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
