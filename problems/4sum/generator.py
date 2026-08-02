from __future__ import annotations
import json
import random

def solve(nums: list[int], target: int) -> list[list[int]]:
    nums.sort()
    n = len(nums)
    res = []
    for i in range(n):
        if i and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s == target:
                    res.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(4, 12)
        nums = [rng.randint(-20, 20) for _ in range(n)]
        target = rng.randint(-40, 40)
        yield {
            "input": f"{json.dumps(nums)}\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(nums[:], target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
