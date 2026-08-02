from __future__ import annotations
import json
import random
from collections import deque

def solve(graph: list[list[int]]) -> bool:
    n = len(graph)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        [[]],
        [[1], [0]],
        [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]],
        [[1, 3], [0, 2], [1, 3], [0, 2]],
        [[], [], []],
        [[1], [0, 2], [1]],
        [[1, 2], [0], [0]],  # triangle — not bipartite
    ]
    for offset in range(count):
        if offset < len(edges):
            g = [row[:] for row in edges[offset]]
        else:
            n = rng.randint(1, 10)
            edge_set = set()
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < 0.25:
                        edge_set.add((i, j))
            g = [[] for _ in range(n)]
            for a, b in edge_set:
                g[a].append(b)
                g[b].append(a)
        yield {
            "input": json.dumps(g),
            "expected_output": json.dumps(solve(g)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
