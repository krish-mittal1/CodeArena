from __future__ import annotations
import json
import random

def solve(s: str) -> bool:
    stack = []
    pair = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pair[ch]:
                return False
            stack.pop()
    return not stack


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    opens = "([{"
    closes = ")]}"
    for offset in range(count):
        if rng.random() < 0.5:
            # mostly valid
            parts = []
            for _ in range(rng.randint(0, 8)):
                i = rng.randint(0, 2)
                parts.append(opens[i] + closes[i])
            s = "".join(parts)
            if rng.random() < 0.3:
                s = "(" + s + ")"
        else:
            s = "".join(rng.choice("()[]{}") for _ in range(rng.randint(1, 16)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
