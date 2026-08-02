from __future__ import annotations
import json
import random

def solve(s: str) -> str:
    return " ".join(reversed(s.split()))


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    words_pool = ["the", "sky", "is", "blue", "hello", "world", "a", "good", "example", "code"]
    for offset in range(count):
        words = [rng.choice(words_pool) for _ in range(rng.randint(1, 8))]
        gaps = [" " * rng.randint(1, 3) for _ in range(len(words) - 1)]
        s = (" " * rng.randint(0, 2))
        for i, w in enumerate(words):
            s += w
            if i < len(gaps):
                s += gaps[i]
        s += " " * rng.randint(0, 2)
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
