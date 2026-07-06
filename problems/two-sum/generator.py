"""Bulk hidden test cases for Two Sum."""

from __future__ import annotations

import json
import random


def solve(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for idx, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], idx]
        seen[value] = idx
    return []


def _encode(nums: list[int], target: int) -> str:
    return f"{json.dumps(nums)}\n{json.dumps(target)}"


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(2, 220)
        nums = [rng.randint(-10**6, 10**6) for _ in range(n)]
        i = rng.randrange(n)
        j = rng.randrange(n)
        while j == i:
            j = rng.randrange(n)
        target = nums[i] + nums[j]
        expected = solve(nums, target)
        yield {
            "input": _encode(nums, target),
            "expected_output": json.dumps(expected),
            "order_index": start_index + offset,
            "is_sample": False,
        }
