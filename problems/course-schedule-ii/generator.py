from __future__ import annotations
import json
import random
from collections import deque
from collections import Counter, defaultdict

def solve(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    from collections import defaultdict, deque
    g = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(numCourses) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == numCourses else []


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 10)
        edges = []
        for a in range(n):
            for b in range(a):
                if rng.random() < 0.2:
                    edges.append([a, b])  # DAG-ish
        if rng.random() < 0.2 and n >= 2:
            edges.append([0, 1])
            edges.append([1, 0])
        yield {
            "input": f"{json.dumps(n)}\n{json.dumps(edges)}",
            "expected_output": json.dumps(solve(n, edges)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
