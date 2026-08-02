from __future__ import annotations
import json
import random

def solve(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    seen = [False] * n
    def dfs(i):
        for j in range(n):
            if isConnected[i][j] and not seen[j]:
                seen[j] = True
                dfs(j)
    provinces = 0
    for i in range(n):
        if not seen[i]:
            seen[i] = True
            dfs(i)
            provinces += 1
    return provinces


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        [[1]],
        [[1, 1], [1, 1]],
        [[1, 0], [0, 1]],
        [[1, 1, 0], [1, 1, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
    ]
    for offset in range(count):
        if offset < len(edges):
            g = [row[:] for row in edges[offset]]
        else:
            n = rng.randint(1, 12)
            g = [[0] * n for _ in range(n)]
            for i in range(n):
                g[i][i] = 1
                for j in range(i + 1, n):
                    if rng.random() < 0.25:
                        g[i][j] = g[j][i] = 1
        yield {
            "input": json.dumps(g),
            "expected_output": json.dumps(solve(g)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
