from __future__ import annotations
import json
import random
from collections import deque

def solve(heights: list[list[int]]) -> list[list[int]]:
    m, n = len(heights), len(heights[0])
    def bfs(starts):
        seen = set(starts)
        q = deque(starts)
        while q:
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return seen
    pac = [(0, j) for j in range(n)] + [(i, 0) for i in range(1, m)]
    atl = [(m - 1, j) for j in range(n)] + [(i, n - 1) for i in range(m - 1)]
    both = bfs(pac) & bfs(atl)
    return sorted([list(p) for p in both])


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        [[1]],
        [[1, 2], [4, 3]],
        [[1, 1], [1, 1], [1, 1]],
        [[10, 10, 10], [10, 1, 10], [10, 10, 10]],
        [[5, 4, 3], [4, 3, 2], [3, 2, 1]],
        [[1, 2, 3], [8, 9, 4], [7, 6, 5]],
        [[3, 3, 3, 3], [3, 0, 0, 3], [3, 0, 0, 3], [3, 3, 3, 3]],
        [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]],
    ]
    for offset in range(count):
        if offset < len(edges):
            heights = [row[:] for row in edges[offset]]
        else:
            m, n = rng.randint(1, 12), rng.randint(1, 12)
            mode = rng.choice(["flat", "random", "ridge", "bowl"])
            if mode == "flat":
                v = rng.randint(0, 20)
                heights = [[v] * n for _ in range(m)]
            elif mode == "ridge":
                heights = [[abs(i - m // 2) + abs(j - n // 2) for j in range(n)] for i in range(m)]
            elif mode == "bowl":
                heights = [[(i + j) % 7 for j in range(n)] for i in range(m)]
            else:
                heights = [[rng.randint(0, 50) for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(heights),
            "expected_output": json.dumps(solve(heights)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
