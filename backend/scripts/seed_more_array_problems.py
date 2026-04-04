from __future__ import annotations

import asyncio
import random
from itertools import pairwise

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TARGET_CASES = 540


def solve_contains_duplicate(nums: list[int]) -> bool:
    return len(set(nums)) != len(nums)


def build_contains_duplicate_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 2, 3, 1], True),
        ([1, 2, 3, 4], False),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums, expected in [
        ([], False),
        ([1], False),
        ([0, 0], True),
        ([-1, -2, -3, -1], True),
        (list(range(20)), False),
        ([5] * 50, True),
        (list(range(-25, 25)) + [7], True),
        ([10**9, -10**9, 10**9], True),
        ([2, 1, 3, 5, 4], False),
        ([3, 3, 2, 2, 1], True),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040401)
    while len(cases) < TARGET_CASES:
        length = rng.randint(0, 220)
        nums = [rng.randint(-10**6, 10**6) for _ in range(length)]
        if nums and rng.random() < 0.55:
            nums[rng.randrange(len(nums))] = nums[rng.randrange(len(nums))]
        cases.append(make_case(nums, expected_output=solve_contains_duplicate(nums), idx=idx))
        idx += 1
    return cases


def solve_missing_number(nums: list[int]) -> int:
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)


def build_missing_number_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([3, 0, 1], 2),
        ([0, 1], 2),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], 0),
        ([0], 1),
        ([1], 0),
        ([0, 2], 1),
        ([1, 2, 3], 0),
        ([0, 1, 2], 3),
        ([4, 2, 1, 0], 3),
        ([5, 4, 3, 2, 1, 0], 6),
        ([9, 6, 4, 2, 3, 5, 7, 0, 1], 8),
        ([2, 0], 1),
    ]
    for nums, expected in fixed:
        cases.append(make_case(nums, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040402)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 260)
        missing = rng.randint(0, n)
        nums = [value for value in range(n + 1) if value != missing]
        rng.shuffle(nums)
        cases.append(make_case(nums, expected_output=missing, idx=idx))
        idx += 1
    return cases


def solve_move_zeroes(nums: list[int]) -> list[int]:
    non_zero = [num for num in nums if num != 0]
    return non_zero + [0] * (len(nums) - len(non_zero))


def build_move_zeroes_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([0, 1, 0, 3, 12], [1, 3, 12, 0, 0]),
        ([0], [0]),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [],
        [1],
        [1, 2, 3],
        [0, 0, 0],
        [4, 0, 5, 0, 0, 3, 0, 1],
        [0, 1, 0, 0, 2, 0, 3],
        [7, 8, 9, 0, 0],
        [-1, 0, -2, 0, -3],
        [0, -1, 0, -2, 0],
        [1, 0, 2, 0, 3, 0, 4, 0, 5],
    ]:
        cases.append(make_case(nums, expected_output=solve_move_zeroes(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040403)
    while len(cases) < TARGET_CASES:
        nums = [0 if rng.random() < 0.35 else rng.randint(-200, 200) for _ in range(rng.randint(0, 220))]
        cases.append(make_case(nums, expected_output=solve_move_zeroes(nums), idx=idx))
        idx += 1
    return cases


def solve_summary_ranges(nums: list[int]) -> list[str]:
    if not nums:
        return []
    ranges: list[str] = []
    start = nums[0]
    prev = nums[0]
    for value in nums[1:]:
        if value == prev + 1:
            prev = value
            continue
        ranges.append(str(start) if start == prev else f"{start}->{prev}")
        start = prev = value
    ranges.append(str(start) if start == prev else f"{start}->{prev}")
    return ranges


def build_summary_ranges_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([0, 1, 2, 4, 5, 7], ["0->2", "4->5", "7"]),
        ([0, 2, 3, 4, 6, 8, 9], ["0", "2->4", "6", "8->9"]),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [],
        [1],
        [1, 2, 3, 4],
        [1, 3, 5, 7],
        [-3, -2, -1, 1, 2, 4],
        [0, 1, 3, 4, 5, 7, 8, 10],
        [-10, -9, -8, -5, 0, 1],
        [100, 101, 102, 200],
        [-1, 0, 1, 2, 50, 51],
        [5, 7],
    ]:
        cases.append(make_case(nums, expected_output=solve_summary_ranges(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040404)
    while len(cases) < TARGET_CASES:
        length = rng.randint(0, 120)
        values = sorted(rng.sample(range(-1000, 1001), length))
        cases.append(make_case(values, expected_output=solve_summary_ranges(values), idx=idx))
        idx += 1
    return cases


def solve_plus_one(digits: list[int]) -> list[int]:
    out = digits[:]
    carry = 1
    for index in range(len(out) - 1, -1, -1):
        total = out[index] + carry
        out[index] = total % 10
        carry = total // 10
    if carry:
        out.insert(0, carry)
    return out


def build_plus_one_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for digits, expected in [
        ([1, 2, 3], [1, 2, 4]),
        ([9], [1, 0]),
    ]:
        cases.append(make_case(digits, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for digits in [
        [0],
        [9, 9],
        [4, 3, 2, 1],
        [1, 9, 9, 9],
        [8, 9, 9, 9, 9],
        [2, 0, 0],
        [9, 0, 9],
        [1, 0, 0, 0, 0],
        [9, 9, 9, 9, 9, 9],
        [5, 6, 7, 8, 9],
    ]:
        cases.append(make_case(digits, expected_output=solve_plus_one(digits), idx=idx))
        idx += 1
    rng = random.Random(2026040405)
    while len(cases) < TARGET_CASES:
        digits = [rng.randint(0, 9) for _ in range(rng.randint(1, 160))]
        if digits[0] == 0 and len(digits) > 1:
            digits[0] = rng.randint(1, 9)
        cases.append(make_case(digits, expected_output=solve_plus_one(digits), idx=idx))
        idx += 1
    return cases


def solve_third_max(nums: list[int]) -> int:
    distinct = sorted(set(nums), reverse=True)
    return distinct[2] if len(distinct) >= 3 else distinct[0]


def build_third_max_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([3, 2, 1], 1),
        ([1, 2], 2),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [2, 2, 3, 1],
        [1, 2, 2, 5, 3, 5],
        [1, 1, 1],
        [-1, -2, -3, -4],
        [10, 9, 8, 7, 6],
        [1, 2, 3, 3],
        [5, 2, 2],
        [7, 8, 9],
        [100, 100, 99, 98],
        [0, -1, -2],
    ]:
        cases.append(make_case(nums, expected_output=solve_third_max(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040406)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(-5000, 5000) for _ in range(rng.randint(1, 220))]
        cases.append(make_case(nums, expected_output=solve_third_max(nums), idx=idx))
        idx += 1
    return cases


def solve_find_disappeared(nums: list[int]) -> list[int]:
    seen = set(nums)
    return [value for value in range(1, len(nums) + 1) if value not in seen]


def build_find_disappeared_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([4, 3, 2, 7, 8, 2, 3, 1], [5, 6]),
        ([1, 1], [2]),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [1],
        [1, 2, 3, 4],
        [2, 2],
        [2, 1, 2, 1],
        [5, 4, 6, 7, 9, 3, 10, 9, 5, 6],
        [1, 1, 1, 1],
        [2, 3, 2, 1, 5, 5],
        [4, 4, 4, 4],
        [3, 3, 3, 3, 3],
        [1, 2, 2, 4, 5, 6, 7, 8],
    ]:
        cases.append(make_case(nums, expected_output=solve_find_disappeared(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040407)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 220)
        nums = [rng.randint(1, n) for _ in range(n)]
        cases.append(make_case(nums, expected_output=solve_find_disappeared(nums), idx=idx))
        idx += 1
    return cases


def solve_array_partition(nums: list[int]) -> int:
    ordered = sorted(nums)
    return sum(ordered[::2])


def build_array_partition_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 4, 3, 2], 4),
        ([6, 2, 6, 5, 1, 2], 9),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [1, 2],
        [-1, 0],
        [9, 8, 7, 6],
        [1, 1, 1, 1],
        [-5, -2, -3, -4],
        [100, -100, 50, -50],
        [3, 5, 2, 3],
        [7, 3, 1, 0, 9, 5],
        [2, 2, 2, 2, 2, 2],
        [-10, 10, -20, 20],
    ]:
        cases.append(make_case(nums, expected_output=solve_array_partition(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040408)
    while len(cases) < TARGET_CASES:
        length = rng.randint(1, 110) * 2
        nums = [rng.randint(-10**4, 10**4) for _ in range(length)]
        cases.append(make_case(nums, expected_output=solve_array_partition(nums), idx=idx))
        idx += 1
    return cases


def solve_sorted_squares(nums: list[int]) -> list[int]:
    return sorted(num * num for num in nums)


def build_sorted_squares_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([-4, -1, 0, 3, 10], [0, 1, 9, 16, 100]),
        ([-7, -3, 2, 3, 11], [4, 9, 9, 49, 121]),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [],
        [0],
        [-1],
        [1],
        [-5, -4, -3, -2, -1],
        [1, 2, 3, 4, 5],
        [-2, -1, 0, 0, 1, 2],
        [-100, -50, 0, 50, 100],
        [-3, -3, -2, 1],
        [-9, -2, 2, 3],
    ]:
        cases.append(make_case(nums, expected_output=solve_sorted_squares(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040409)
    while len(cases) < TARGET_CASES:
        nums = sorted(rng.randint(-10**4, 10**4) for _ in range(rng.randint(0, 220)))
        cases.append(make_case(nums, expected_output=solve_sorted_squares(nums), idx=idx))
        idx += 1
    return cases


def solve_height_checker(heights: list[int]) -> int:
    return sum(a != b for a, b in zip(heights, sorted(heights)))


def build_height_checker_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for heights, expected in [
        ([1, 1, 4, 2, 1, 3], 3),
        ([5, 1, 2, 3, 4], 5),
    ]:
        cases.append(make_case(heights, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for heights in [
        [],
        [1],
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [5, 5, 5, 5],
        [1, 2, 1, 2, 1, 2],
        [10, 9, 8, 7, 6, 5],
        [1, 1, 1, 2, 2, 2],
        [3, 2, 3, 2, 3],
        [100, 1, 100, 1],
    ]:
        cases.append(make_case(heights, expected_output=solve_height_checker(heights), idx=idx))
        idx += 1
    rng = random.Random(2026040410)
    while len(cases) < TARGET_CASES:
        heights = [rng.randint(1, 100) for _ in range(rng.randint(0, 220))]
        cases.append(make_case(heights, expected_output=solve_height_checker(heights), idx=idx))
        idx += 1
    return cases


def solve_replace_elements(arr: list[int]) -> list[int]:
    best = -1
    out = arr[:]
    for index in range(len(out) - 1, -1, -1):
        out[index], best = best, max(best, out[index])
    return out


def build_replace_elements_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for arr, expected in [
        ([17, 18, 5, 4, 6, 1], [18, 6, 6, 6, 1, -1]),
        ([400], [-1]),
    ]:
        cases.append(make_case(arr, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for arr in [
        [],
        [1],
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [5, 5, 5],
        [0, 0, 0],
        [9, 1, 8, 2, 7, 3],
        [100, 1, 50, 2],
        [2, 1],
        [6, 4, 3, 1, 5],
    ]:
        cases.append(make_case(arr, expected_output=solve_replace_elements(arr), idx=idx))
        idx += 1
    rng = random.Random(2026040411)
    while len(cases) < TARGET_CASES:
        arr = [rng.randint(0, 10**5) for _ in range(rng.randint(0, 220))]
        cases.append(make_case(arr, expected_output=solve_replace_elements(arr), idx=idx))
        idx += 1
    return cases


def solve_pivot_index(nums: list[int]) -> int:
    total = sum(nums)
    left = 0
    for index, value in enumerate(nums):
        if left == total - left - value:
            return index
        left += value
    return -1


def build_pivot_index_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 7, 3, 6, 5, 6], 3),
        ([1, 2, 3], -1),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [2, 1, -1],
        [0],
        [0, 0, 0, 0],
        [-1, -1, -1, -1, -1, 0],
        [10, -10, 10, -10, 10, -10, 0],
        [1, -1, 0],
        [20, 10, -30, 10, 20],
        [1, 1, 1, 1, 4],
        [5, -2, -1, -1, -1],
        [100, 0, -100],
    ]:
        cases.append(make_case(nums, expected_output=solve_pivot_index(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040412)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(-1000, 1000) for _ in range(rng.randint(1, 220))]
        cases.append(make_case(nums, expected_output=solve_pivot_index(nums), idx=idx))
        idx += 1
    return cases


def solve_stock_ii(prices: list[int]) -> int:
    return sum(max(0, b - a) for a, b in pairwise(prices))


def build_stock_ii_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for prices, expected in [
        ([7, 1, 5, 3, 6, 4], 7),
        ([1, 2, 3, 4, 5], 4),
    ]:
        cases.append(make_case(prices, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for prices in [
        [],
        [1],
        [7, 6, 4, 3, 1],
        [1, 2],
        [2, 1, 2, 0, 1],
        [3, 3, 3],
        [1, 7, 2, 8, 3, 9],
        [9, 1, 9, 1, 9],
        [2, 4, 1, 5, 2, 6],
        [10, 9, 8, 1, 2, 3],
    ]:
        cases.append(make_case(prices, expected_output=solve_stock_ii(prices), idx=idx))
        idx += 1
    rng = random.Random(2026040413)
    while len(cases) < TARGET_CASES:
        prices = [rng.randint(0, 10**4) for _ in range(rng.randint(0, 220))]
        cases.append(make_case(prices, expected_output=solve_stock_ii(prices), idx=idx))
        idx += 1
    return cases


def solve_find_duplicate(nums: list[int]) -> int:
    slow = nums[0]
    fast = nums[nums[0]]
    while slow != fast:
        slow = nums[slow]
        fast = nums[nums[fast]]
    slow = 0
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


def build_find_duplicate_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 3, 4, 2, 2], 2),
        ([3, 1, 3, 4, 2], 3),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([1, 1], 1),
        ([1, 1, 2], 1),
        ([2, 1, 2], 2),
        ([2, 2, 2, 2, 2], 2),
        ([1, 4, 6, 3, 2, 5, 6], 6),
        ([5, 4, 3, 2, 1, 5], 5),
        ([4, 3, 1, 4, 2], 4),
        ([1, 2, 3, 4, 4], 4),
        ([7, 2, 5, 4, 6, 3, 1, 7], 7),
        ([2, 5, 9, 6, 9, 3, 8, 9, 7, 1], 9),
    ]
    for nums, expected in fixed:
        cases.append(make_case(nums, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040414)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 220)
        duplicate = rng.randint(1, n)
        nums = list(range(1, n + 1)) + [duplicate]
        rng.shuffle(nums)
        cases.append(make_case(nums, expected_output=duplicate, idx=idx))
        idx += 1
    return cases


def solve_monotonic(nums: list[int]) -> bool:
    non_decreasing = all(a <= b for a, b in pairwise(nums))
    non_increasing = all(a >= b for a, b in pairwise(nums))
    return non_decreasing or non_increasing


def build_monotonic_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 2, 2, 3], True),
        ([6, 5, 4, 4], True),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [],
        [1],
        [1, 1, 1],
        [1, 3, 2],
        [3, 2, 2, 1],
        [-5, -4, -4, -1],
        [10, 9, 8, 7],
        [1, 2, 3, 4, 5],
        [1, 1, 0, 1],
        [5, 4, 4, 5],
    ]:
        cases.append(make_case(nums, expected_output=solve_monotonic(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040415)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(-10**5, 10**5) for _ in range(rng.randint(0, 220))]
        if rng.random() < 0.4:
            nums.sort(reverse=rng.random() < 0.5)
        cases.append(make_case(nums, expected_output=solve_monotonic(nums), idx=idx))
        idx += 1
    return cases


def solve_largest_number(nums: list[int]) -> str:
    as_strings = list(map(str, nums))
    as_strings.sort(key=lambda item: item * 10, reverse=True)
    out = "".join(as_strings).lstrip("0")
    return out or "0"


def build_largest_number_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([10, 2], "210"),
        ([3, 30, 34, 5, 9], "9534330"),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [0],
        [0, 0],
        [1],
        [20, 1],
        [121, 12],
        [8308, 8308, 830],
        [432, 43243],
        [999999998, 999999997, 999999999],
        [0, 0, 1],
        [54, 546, 548, 60],
    ]:
        cases.append(make_case(nums, expected_output=solve_largest_number(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040416)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(0, 10**9) for _ in range(rng.randint(1, 90))]
        cases.append(make_case(nums, expected_output=solve_largest_number(nums), idx=idx))
        idx += 1
    return cases


def solve_increasing_triplet(nums: list[int]) -> bool:
    first = second = float("inf")
    for num in nums:
        if num <= first:
            first = num
        elif num <= second:
            second = num
        else:
            return True
    return False


def build_increasing_triplet_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([1, 2, 3, 4, 5], True),
        ([5, 4, 3, 2, 1], False),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [1],
        [1, 2],
        [2, 1, 5, 0, 4, 6],
        [20, 100, 10, 12, 5, 13],
        [5, 1, 5, 5, 2, 5, 4],
        [2, 4, -2, -3],
        [1, 1, 1, 1],
        [-10, -8, -9, -7],
        [9, 1, 8, 2, 7, 3],
        [3, 2, 1, 2, 3],
    ]:
        cases.append(make_case(nums, expected_output=solve_increasing_triplet(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040417)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(-10**5, 10**5) for _ in range(rng.randint(1, 220))]
        cases.append(make_case(nums, expected_output=solve_increasing_triplet(nums), idx=idx))
        idx += 1
    return cases


def solve_min_size_subarray(target: int, nums: list[int]) -> int:
    left = 0
    total = 0
    best = len(nums) + 1
    for right, value in enumerate(nums):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == len(nums) + 1 else best


def build_min_size_subarray_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for target, nums, expected in [
        (7, [2, 3, 1, 2, 4, 3], 2),
        (4, [1, 4, 4], 1),
    ]:
        cases.append(make_case(target, nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        (1, [], 0),
        (100, [1, 2, 3], 0),
        (5, [5], 1),
        (11, [1, 2, 3, 4, 5], 3),
        (15, [1, 2, 3, 4, 5], 5),
        (16, [1, 2, 3, 4, 5], 0),
        (3, [1, 1, 1], 3),
        (6, [2, 2, 2, 2], 3),
        (8, [4, 4, 4], 2),
        (9, [1, 10], 1),
    ]
    for target, nums, expected in fixed:
        cases.append(make_case(target, nums, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040418)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(1, 1000) for _ in range(rng.randint(0, 220))]
        target = rng.randint(1, 4000)
        cases.append(make_case(target, nums, expected_output=solve_min_size_subarray(target, nums), idx=idx))
        idx += 1
    return cases


def solve_shortest_unsorted(nums: list[int]) -> int:
    sorted_nums = sorted(nums)
    left = 0
    while left < len(nums) and nums[left] == sorted_nums[left]:
        left += 1
    if left == len(nums):
        return 0
    right = len(nums) - 1
    while nums[right] == sorted_nums[right]:
        right -= 1
    return right - left + 1


def build_shortest_unsorted_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([2, 6, 4, 8, 10, 9, 15], 5),
        ([1, 2, 3, 4], 0),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [],
        [1],
        [1, 3, 2, 2, 2],
        [2, 1],
        [1, 2, 4, 5, 3],
        [1, 1, 1],
        [1, 2, 3, 3, 3],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 3, 2, 2, 2],
        [10, 12, 15, 14, 13, 16],
    ]:
        cases.append(make_case(nums, expected_output=solve_shortest_unsorted(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040419)
    while len(cases) < TARGET_CASES:
        nums = [rng.randint(-10**4, 10**4) for _ in range(rng.randint(0, 220))]
        if rng.random() < 0.35:
            nums.sort()
        cases.append(make_case(nums, expected_output=solve_shortest_unsorted(nums), idx=idx))
        idx += 1
    return cases


def solve_find_all_duplicates(nums: list[int]) -> list[int]:
    counts: dict[int, int] = {}
    out: list[int] = []
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
        if counts[value] == 2:
            out.append(value)
    return out


def build_find_all_duplicates_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for nums, expected in [
        ([4, 3, 2, 7, 8, 2, 3, 1], [2, 3]),
        ([1, 1, 2], [1]),
    ]:
        cases.append(make_case(nums, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    for nums in [
        [1],
        [1, 2, 3, 4],
        [2, 2],
        [1, 1, 2, 2, 3, 3],
        [5, 4, 6, 7, 9, 3, 10, 9, 5, 6],
        [4, 4, 4, 4],
        [2, 1, 2, 1],
        [3, 3, 3, 1, 2],
        [1, 2, 2, 4, 4, 6],
        [6, 5, 4, 3, 2, 1, 6, 5],
    ]:
        cases.append(make_case(nums, expected_output=solve_find_all_duplicates(nums), idx=idx))
        idx += 1
    rng = random.Random(2026040420)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 220)
        nums = [rng.randint(1, n) for _ in range(n)]
        cases.append(make_case(nums, expected_output=solve_find_all_duplicates(nums), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    {
        "title": "Contains Duplicate",
        "kwargs": {
            "description": "Given an integer array nums, return true if any value appears at least twice and false if every element is distinct.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Boolean indicating whether any duplicate exists",
            "constraints": "0 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
            "method_name": "containsDuplicate",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "bool",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 700,
            "is_active": True,
        },
        "builder": build_contains_duplicate_cases,
    },
    {
        "title": "Missing Number",
        "kwargs": {
            "description": "Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing from the array.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer: the missing number",
            "constraints": "0 <= n <= 10^5\nnums contains unique values from [0, n]",
            "method_name": "missingNumber",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 800,
            "is_active": True,
        },
        "builder": build_missing_number_cases,
    },
    {
        "title": "Move Zeroes",
        "kwargs": {
            "description": "Move all 0's to the end of the array while maintaining the relative order of the non-zero elements.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "JSON array after moving all zeroes to the end",
            "constraints": "0 <= nums.length <= 10^5\n-2^31 <= nums[i] <= 2^31 - 1",
            "method_name": "moveZeroes",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 800,
            "is_active": True,
        },
        "builder": build_move_zeroes_cases,
    },
    {
        "title": "Summary Ranges",
        "kwargs": {
            "description": "Given a sorted unique integer array nums, return the smallest sorted list of ranges that exactly covers all the numbers in the array.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (sorted unique int[])",
            "output_format": "JSON array of strings describing the ranges",
            "constraints": "0 <= nums.length <= 10^5\n-2^31 <= nums[i] <= 2^31 - 1",
            "method_name": "summaryRanges",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "string[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_summary_ranges_cases,
    },
    {
        "title": "Plus One",
        "kwargs": {
            "description": "You are given a large integer represented as an integer array digits. Increment the integer by one and return the resulting array of digits.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array digits (int[])",
            "output_format": "JSON array of digits after adding one",
            "constraints": "1 <= digits.length <= 100\n0 <= digits[i] <= 9",
            "method_name": "plusOne",
            "parameters": [{"name": "digits", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 800,
            "is_active": True,
        },
        "builder": build_plus_one_cases,
    },
    {
        "title": "Third Maximum Number",
        "kwargs": {
            "description": "Given an integer array nums, return the third distinct maximum number in the array. If the third distinct maximum does not exist, return the maximum number.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer result",
            "constraints": "1 <= nums.length <= 10^4\n-2^31 <= nums[i] <= 2^31 - 1",
            "method_name": "thirdMax",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_third_max_cases,
    },
    {
        "title": "Find All Numbers Disappeared in an Array",
        "kwargs": {
            "description": "Given an array nums of length n where each value is in the range [1, n], return all numbers in the range [1, n] that do not appear in nums.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "JSON array of missing numbers in ascending order",
            "constraints": "1 <= nums.length <= 10^5\n1 <= nums[i] <= nums.length",
            "method_name": "findDisappearedNumbers",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_find_disappeared_cases,
    },
    {
        "title": "Array Partition",
        "kwargs": {
            "description": "Given 2n integers, group these integers into n pairs such that the sum of min(ai, bi) for all pairs is maximized.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer: maximum possible sum",
            "constraints": "1 <= nums.length / 2 <= 10^4\nnums.length is even",
            "method_name": "arrayPairSum",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_array_partition_cases,
    },
    {
        "title": "Squares of a Sorted Array",
        "kwargs": {
            "description": "Given an integer array nums sorted in non-decreasing order, return an array of the squares of each number sorted in non-decreasing order.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (sorted int[])",
            "output_format": "JSON array of sorted squares",
            "constraints": "0 <= nums.length <= 10^4\n-10^4 <= nums[i] <= 10^4",
            "method_name": "sortedSquares",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_sorted_squares_cases,
    },
    {
        "title": "Height Checker",
        "kwargs": {
            "description": "Return the number of indices where the current heights array differs from the array sorted in non-decreasing order.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array heights (int[])",
            "output_format": "Single integer mismatch count",
            "constraints": "0 <= heights.length <= 100\n1 <= heights[i] <= 100",
            "method_name": "heightChecker",
            "parameters": [{"name": "heights", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 800,
            "is_active": True,
        },
        "builder": build_height_checker_cases,
    },
    {
        "title": "Replace Elements with Greatest Element on Right Side",
        "kwargs": {
            "description": "Replace every element in the array with the greatest element among the elements to its right, and replace the last element with -1.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array arr (int[])",
            "output_format": "JSON array after replacement",
            "constraints": "0 <= arr.length <= 10^4\n1 <= arr[i] <= 10^5",
            "method_name": "replaceElements",
            "parameters": [{"name": "arr", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_replace_elements_cases,
    },
    {
        "title": "Find Pivot Index",
        "kwargs": {
            "description": "Return the leftmost pivot index of the array where the sum of the numbers strictly to the left equals the sum strictly to the right. Return -1 if no pivot index exists.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer pivot index or -1",
            "constraints": "1 <= nums.length <= 10^4\n-1000 <= nums[i] <= 1000",
            "method_name": "pivotIndex",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 900,
            "is_active": True,
        },
        "builder": build_pivot_index_cases,
    },
    {
        "title": "Best Time to Buy and Sell Stock II",
        "kwargs": {
            "description": "You may buy and sell the stock multiple times. Return the maximum profit you can achieve.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array prices (int[])",
            "output_format": "Single integer maximum profit",
            "constraints": "0 <= prices.length <= 3 * 10^4\n0 <= prices[i] <= 10^4",
            "method_name": "maxProfit",
            "parameters": [{"name": "prices", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1000,
            "is_active": True,
        },
        "builder": build_stock_ii_cases,
    },
    {
        "title": "Find the Duplicate Number",
        "kwargs": {
            "description": "Given an array of n + 1 integers where each integer is in the range [1, n] inclusive, return the duplicated number.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer duplicated value",
            "constraints": "1 <= n <= 10^5\nnums.length == n + 1\n1 <= nums[i] <= n",
            "method_name": "findDuplicate",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1200,
            "is_active": True,
        },
        "builder": build_find_duplicate_cases,
    },
    {
        "title": "Monotonic Array",
        "kwargs": {
            "description": "Return true if the array is monotone increasing or monotone decreasing.",
            "difficulty": Difficulty.EASY,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Boolean indicating whether the array is monotonic",
            "constraints": "0 <= nums.length <= 10^5\n-10^5 <= nums[i] <= 10^5",
            "method_name": "isMonotonic",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "bool",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 800,
            "is_active": True,
        },
        "builder": build_monotonic_cases,
    },
    {
        "title": "Largest Number",
        "kwargs": {
            "description": "Given a list of non-negative integers nums, arrange them such that they form the largest possible number and return it as a string.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "String representing the largest concatenated number",
            "constraints": "1 <= nums.length <= 100\n0 <= nums[i] <= 10^9",
            "method_name": "largestNumber",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "string",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1200,
            "is_active": True,
        },
        "builder": build_largest_number_cases,
    },
    {
        "title": "Increasing Triplet Subsequence",
        "kwargs": {
            "description": "Return true if there exists a triple of indices i < j < k such that nums[i] < nums[j] < nums[k].",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Boolean indicating whether an increasing triplet exists",
            "constraints": "1 <= nums.length <= 5 * 10^5\n-2^31 <= nums[i] <= 2^31 - 1",
            "method_name": "increasingTriplet",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "bool",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1200,
            "is_active": True,
        },
        "builder": build_increasing_triplet_cases,
    },
    {
        "title": "Minimum Size Subarray Sum",
        "kwargs": {
            "description": "Given an array of positive integers nums and a positive integer target, return the minimal length of a subarray whose sum is greater than or equal to target. Return 0 if there is no such subarray.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: integer target\nLine 2: JSON array nums (positive int[])",
            "output_format": "Single integer minimum subarray length",
            "constraints": "0 <= nums.length <= 10^5\n1 <= nums[i] <= 10^4\n1 <= target <= 10^9",
            "method_name": "minSubArrayLen",
            "parameters": [{"name": "target", "type": "int"}, {"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1200,
            "is_active": True,
        },
        "builder": build_min_size_subarray_cases,
    },
    {
        "title": "Shortest Unsorted Continuous Subarray",
        "kwargs": {
            "description": "Return the length of the shortest continuous subarray such that sorting only that subarray would make the whole array sorted in non-decreasing order.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "Single integer subarray length",
            "constraints": "0 <= nums.length <= 10^4\n-10^5 <= nums[i] <= 10^5",
            "method_name": "findUnsortedSubarray",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1300,
            "is_active": True,
        },
        "builder": build_shortest_unsorted_cases,
    },
    {
        "title": "Find All Duplicates in an Array",
        "kwargs": {
            "description": "Given an integer array nums of length n where all the integers are in the range [1, n], return all the integers that appear twice.",
            "difficulty": Difficulty.MEDIUM,
            "input_format": "Line 1: JSON array nums (int[])",
            "output_format": "JSON array of duplicates in ascending encounter order",
            "constraints": "1 <= nums.length <= 10^5\n1 <= nums[i] <= nums.length",
            "method_name": "findDuplicates",
            "parameters": [{"name": "nums", "type": "int[]"}],
            "return_type": "int[]",
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "rating": 1200,
            "is_active": True,
        },
        "builder": build_find_all_duplicates_cases,
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        for problem in PROBLEMS:
            await upsert_problem(db, problem["title"], problem["kwargs"], problem["builder"]())
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
