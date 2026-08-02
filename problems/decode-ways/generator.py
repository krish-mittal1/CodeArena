from __future__ import annotations
import json
import random

def solve(s: str) -> int:
    if not s or s[0] == "0":
        return 0
    n = len(s)
    dp0, dp1 = 1, 1
    for i in range(1, n):
        cur = 0
        if s[i] != "0":
            cur += dp1
        two = int(s[i - 1:i + 1])
        if 10 <= two <= 26:
            cur += dp0
        dp0, dp1 = dp1, cur
    return dp1


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        s = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(1, 20)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
