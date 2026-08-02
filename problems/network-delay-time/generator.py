from __future__ import annotations
import json
import random
import heapq

def solve(times: list[list[int]], n: int, k: int) -> int:
    g = [[] for _ in range(n + 1)]
    for u, v, w in times:
        g[u].append((v, w))
    dist = [10**18] * (n + 1)
    dist[k] = 0
    pq = [(0, k)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    ans = max(dist[1:])
    return -1 if ans >= 10**18 else ans


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        ([[1, 2, 1]], 2, 1),
        ([[1, 2, 1]], 2, 2),
        ([], 1, 1),
        ([[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1),
        ([[1, 2, 1], [2, 1, 3]], 2, 2),
        ([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2),
        ([[1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 5, 1]], 5, 1),
        ([[1, 2, 1], [2, 3, 1], [3, 1, 1]], 3, 1),  # cycle
        ([[1, 2, 100], [1, 3, 1], [3, 2, 1]], 3, 1),  # shorter via 3
        ([[5, 4, 1]], 5, 5),  # unreachable others
    ]
    for offset in range(count):
        if offset < len(edges):
            times, n, k = edges[offset]
            times = [e[:] for e in times]
        else:
            n = rng.randint(1, 20)
            times = []
            mode = rng.choice(["sparse", "dense", "line", "star"])
            if mode == "line" and n >= 2:
                for i in range(1, n):
                    times.append([i, i + 1, rng.randint(1, 10)])
            elif mode == "star" and n >= 2:
                hub = rng.randint(1, n)
                for i in range(1, n + 1):
                    if i != hub:
                        times.append([hub, i, rng.randint(1, 10)])
            else:
                edge_count = rng.randint(0, n * (3 if mode == "dense" else 2))
                for _ in range(edge_count):
                    u, v = rng.randint(1, n), rng.randint(1, n)
                    if u != v:
                        times.append([u, v, rng.randint(1, 50)])
            k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(times)}\n{json.dumps(n)}\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(times, n, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
