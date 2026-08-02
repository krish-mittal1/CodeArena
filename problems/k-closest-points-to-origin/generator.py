from __future__ import annotations
import json
import random
import heapq

def solve(points: list[list[int]], k: int) -> list[list[int]]:
    return heapq.nsmallest(k, points, key=lambda p: p[0]*p[0] + p[1]*p[1])


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 20)
        # unique distances
        points = []
        used = set()
        while len(points) < n:
            x, y = rng.randint(-20, 20), rng.randint(-20, 20)
            d = x*x + y*y
            if d in used:
                continue
            used.add(d)
            points.append([x, y])
        k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(points)}\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(points, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
