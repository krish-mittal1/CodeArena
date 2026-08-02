from __future__ import annotations
import json
import random

def solve(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            cur = dp[j]
            if text1[i - 1] == text2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[n]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcdefghij"
    for offset in range(count):
        a = "".join(rng.choice(letters) for _ in range(rng.randint(1, 30)))
        b = "".join(rng.choice(letters) for _ in range(rng.randint(1, 30)))
        yield {
            "input": f"{json.dumps(a)}\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
