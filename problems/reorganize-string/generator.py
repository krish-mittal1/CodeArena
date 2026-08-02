from __future__ import annotations
import json
import random
import heapq
from collections import Counter, defaultdict

def solve(s: str) -> str:
    cnt = Counter(s)
    heap = [(-c, ch) for ch, c in cnt.items()]
    heapq.heapify(heap)
    res = []
    prev = None
    while heap:
        c, ch = heapq.heappop(heap)
        res.append(ch)
        if prev:
            heapq.heappush(heap, prev)
        c += 1
        prev = (c, ch) if c < 0 else None
    ans = "".join(res)
    return ans if len(ans) == len(s) else ""


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcde"
    for offset in range(count):
        s = "".join(rng.choice(letters) for _ in range(rng.randint(1, 20)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
