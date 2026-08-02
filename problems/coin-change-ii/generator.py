from __future__ import annotations
import json
import random

def solve(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        coins = sorted({rng.randint(1, 20) for _ in range(rng.randint(1, 5))})
        amount = rng.randint(0, 80)
        yield {
            "input": f"{json.dumps(amount)}\n{json.dumps(coins)}",
            "expected_output": json.dumps(solve(amount, coins)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
