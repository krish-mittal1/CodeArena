from __future__ import annotations
import json
import random

def solve(coins: list[int], amount: int) -> int:
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] <= amount else -1

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(1, 8)
        coins = sorted({rng.randint(1, 50) for _ in range(k)})
        amount = rng.randint(0, 200)
        yield {
            "input": f"{json.dumps(coins)}\n{json.dumps(amount)}",
            "expected_output": json.dumps(solve(coins, amount)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
