from __future__ import annotations
import json
import random

def solve(nums: list[int]) -> list[list[int]]:
    res = []
    def dfs(path, used):
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(x)
            dfs(path, used)
            path.pop()
            used[i] = False
    dfs([], [False] * len(nums))
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 5)
        nums = rng.sample(range(-9, 10), n)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
