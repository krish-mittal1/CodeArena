"""Bulk hidden test cases for Valid Palindrome."""

from __future__ import annotations

import json
import random
import string


def solve(s: str) -> bool:
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    alphabet = string.ascii_letters + string.digits + " ,.:;!?-_"
    for offset in range(count):
        n = rng.randint(0, 200)
        s = "".join(alphabet[rng.randint(0, len(alphabet) - 1)] for _ in range(n))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
