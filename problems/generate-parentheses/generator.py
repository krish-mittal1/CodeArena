from __future__ import annotations
import json
import random

def solve(n: int) -> list[str]:
    res = []
    def dfs(s, opens, closes):
        if len(s) == 2 * n:
            res.append(s)
            return
        if opens < n:
            dfs(s + "(", opens + 1, closes)
        if closes < opens:
            dfs(s + ")", opens, closes + 1)
    dfs("", 0, 0)
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    for offset, n in enumerate(range(1, min(count, 8) + 1)):
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
