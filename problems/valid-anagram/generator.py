"""Bulk hidden test cases for Valid Anagram."""

from __future__ import annotations

import json
import random


def solve(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)


def encode(s: str, t: str) -> str:
    return f"{json.dumps(s)}\n{json.dumps(t)}"


def rand_word(rng: random.Random, length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join(rng.choice(alphabet) for _ in range(length))


FIXED = [
    ("a", "a"),
    ("ab", "ba"),
    ("ab", "aa"),
    ("listen", "silent"),
    ("triangle", "integral"),
    ("hello", "bello"),
    ("aaabbb", "bbbaaa"),
    ("zzz", "zzzz"),
]


def generate_cases(*, count: int, seed: int, start_index: int):
    idx = start_index
    for s, t in FIXED:
        yield {
            "input": encode(s, t),
            "expected_output": json.dumps(solve(s, t)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1

    rng = random.Random(seed)
    generated = 0
    while generated < count:
        length = rng.randint(0, 60)
        s = rand_word(rng, length)
        if rng.random() < 0.65:
            chars = list(s)
            rng.shuffle(chars)
            t = "".join(chars)
        else:
            t = rand_word(rng, rng.randint(max(0, length - 2), length + 2))
        yield {
            "input": encode(s, t),
            "expected_output": json.dumps(solve(s, t)),
            "order_index": idx,
            "is_sample": False,
        }
        idx += 1
        generated += 1
