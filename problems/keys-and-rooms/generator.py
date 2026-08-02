from __future__ import annotations
import json
import random

def solve(rooms: list[list[int]]) -> bool:
    n = len(rooms)
    seen = [False] * n
    stack = [0]
    seen[0] = True
    while stack:
        u = stack.pop()
        for v in rooms[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return all(seen)

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 30)
        rooms = [[] for _ in range(n)]
        if rng.random() < 0.6 and n > 1:
            for i in range(n - 1):
                rooms[i].append(i + 1)
        for i in range(n):
            for _ in range(rng.randint(0, 3)):
                k = rng.randrange(n)
                if k not in rooms[i]:
                    rooms[i].append(k)
        yield {
            "input": json.dumps(rooms),
            "expected_output": json.dumps(solve(rooms)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
