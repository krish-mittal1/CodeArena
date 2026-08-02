from __future__ import annotations
import json
import random

_MAP = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}

def solve(digits: str) -> list[str]:
    if not digits:
        return []
    res = [""]
    for d in digits:
        res = [p + c for p in res for c in _MAP[d]]
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        digits = "".join(rng.choice("23456789") for _ in range(rng.randint(0, 4)))
        yield {
            "input": json.dumps(digits),
            "expected_output": json.dumps(solve(digits)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
