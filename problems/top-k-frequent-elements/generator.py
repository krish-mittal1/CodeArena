from __future__ import annotations
import json
import random
from collections import Counter, defaultdict

def solve(nums: list[int], k: int) -> list[int]:
    cnt = Counter(nums)
    return [x for x, _ in cnt.most_common(k)]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        uniq = len(set(nums))
        k = rng.randint(1, max(1, uniq))
        yield {
            "input": f"{json.dumps(nums)}\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
