from __future__ import annotations
import json
import random
import heapq

def solve(stones: list[int]) -> int:
    h = [-s for s in stones]
    heapq.heapify(h)
    while len(h) > 1:
        y = -heapq.heappop(h)
        x = -heapq.heappop(h)
        if y != x:
            heapq.heappush(h, -(y - x))
    return -h[0] if h else 0


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        stones = [rng.randint(1, 100) for _ in range(rng.randint(1, 20))]
        yield {
            "input": json.dumps(stones),
            "expected_output": json.dumps(solve(stones)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
