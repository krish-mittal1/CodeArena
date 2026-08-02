from __future__ import annotations
import json
import random
from collections import Counter, defaultdict

def solve(s: str, p: str) -> list[int]:
    if len(p) > len(s):
        return []
    need = Counter(p)
    window = Counter()
    res = []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            left = s[i - len(p)]
            window[left] -= 1
            if window[left] == 0:
                del window[left]
        if i >= len(p) - 1 and window == need:
            res.append(i - len(p) + 1)
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcde"
    for offset in range(count):
        s = "".join(rng.choice(letters) for _ in range(rng.randint(1, 40)))
        p = "".join(rng.choice(letters) for _ in range(rng.randint(1, 5)))
        yield {
            "input": f"{json.dumps(s)}\n{json.dumps(p)}",
            "expected_output": json.dumps(solve(s, p)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
