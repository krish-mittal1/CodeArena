from __future__ import annotations
import json
import random

def solve(s: str, t: str) -> bool:
    i = 0
    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1
    return i == len(s)


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcd"
    for offset in range(count):
        t = "".join(rng.choice(letters) for _ in range(rng.randint(0, 30)))
        if rng.random() < 0.5 and t:
            s = "".join(t[i] for i in sorted(rng.sample(range(len(t)), rng.randint(0, len(t)))))
        else:
            s = "".join(rng.choice(letters) for _ in range(rng.randint(0, 8)))
        yield {
            "input": f"{json.dumps(s)}\n{json.dumps(t)}",
            "expected_output": json.dumps(solve(s, t)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
