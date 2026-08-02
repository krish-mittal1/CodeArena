from __future__ import annotations
import json
import random
from collections import deque

def solve(numCourses: int, prerequisites: list[list[int]]) -> bool:
    indeg = [0] * numCourses
    g = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(numCourses) if indeg[i] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == numCourses

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        (1, []),
        (2, [[1, 0]]),
        (2, [[1, 0], [0, 1]]),
        (3, [[1, 0], [2, 1]]),
        (3, [[1, 0], [2, 1], [0, 2]]),
        (4, []),
        (4, [[1, 0], [2, 0], [3, 1], [3, 2]]),
        (5, [[1, 0], [2, 1], [3, 2], [4, 3], [1, 4]]),
    ]
    for offset in range(count):
        if offset < len(edges):
            n, prereq = edges[offset]
            prereq = [e[:] for e in prereq]
        else:
            n = rng.randint(1, 40)
            edge_set = set()
            for _ in range(rng.randint(0, n * 2)):
                a = rng.randrange(n)
                b = rng.randrange(n)
                if a == b:
                    continue
                if rng.random() < 0.85 and a < b:
                    a, b = b, a
                edge_set.add((a, b))
            prereq = [list(e) for e in edge_set]
        yield {
            "input": f"{json.dumps(n)}\n{json.dumps(prereq)}",
            "expected_output": json.dumps(solve(n, prereq)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
