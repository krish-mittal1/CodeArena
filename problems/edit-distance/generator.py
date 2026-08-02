from __future__ import annotations
import json
import random

def solve(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            tmp = dp[j]
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = tmp
    return dp[n]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcd"
    for offset in range(count):
        a = "".join(rng.choice(letters) for _ in range(rng.randint(0, 12)))
        b = "".join(rng.choice(letters) for _ in range(rng.randint(0, 12)))
        yield {
            "input": f"{json.dumps(a)}\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
