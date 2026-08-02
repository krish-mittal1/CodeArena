from __future__ import annotations
import json
import random

def solve(candidates: list[int], target: int) -> list[list[int]]:
    candidates = sorted(candidates)
    res = []
    def dfs(start, remain, path):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            dfs(i, remain - c, path)
            path.pop()
    dfs(0, target, [])
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(1, 6)
        candidates = sorted({rng.randint(2, 20) for _ in range(k)})
        target = rng.randint(1, 30)
        ans = solve(candidates, target)
        yield {
            "input": f"{json.dumps(candidates)}\n{json.dumps(target)}",
            "expected_output": json.dumps(ans),
            "order_index": start_index + offset,
            "is_sample": False,
        }
