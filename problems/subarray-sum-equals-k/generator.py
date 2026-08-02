from __future__ import annotations
import json
import random
from collections import Counter, defaultdict

def solve(nums: list[int], k: int) -> int:
    prefix = 0
    cnt = defaultdict(int)
    cnt[0] = 1
    ans = 0
    for x in nums:
        prefix += x
        ans += cnt[prefix - k]
        cnt[prefix] += 1
    return ans


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        k = rng.randint(-20, 20)
        yield {
            "input": f"{json.dumps(nums)}\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
