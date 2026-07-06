"""Bulk hidden test cases for 3 Sum (stdin/stdout CP mode)."""

from __future__ import annotations

import random


def solve_3sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res: list[list[int]] = []
    for i in range(len(nums)):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total > 0:
                right -= 1
            elif total < 0:
                left += 1
            else:
                res.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
    return res


def format_case(nums: list[int]) -> tuple[str, str]:
    input_str = f"{len(nums)}\n" + " ".join(map(str, nums))
    expected_list = solve_3sum(nums)
    output_str = f"{len(expected_list)}"
    for triplet in expected_list:
        output_str += "\n" + " ".join(map(str, triplet))
    return input_str, output_str


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(3, 1000)
        nums = [rng.randint(-1000, 1000) for _ in range(n)]
        inp, out = format_case(nums)
        yield {
            "input": inp,
            "expected_output": out,
            "order_index": start_index + offset,
            "is_sample": False,
        }
