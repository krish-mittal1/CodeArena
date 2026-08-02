from __future__ import annotations
import json
import random

def solve(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    ans = [0] * n
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 50)
        temps = [rng.randint(30, 100) for _ in range(n)]
        yield {
            "input": json.dumps(temps),
            "expected_output": json.dumps(solve(temps)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
