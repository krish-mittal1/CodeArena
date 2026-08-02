from __future__ import annotations
import json
import random
from collections import deque

def solve(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j, 0))
            elif grid[i][j] == 1:
                fresh += 1
    minutes = 0
    while q:
        r, c, t = q.popleft()
        minutes = t
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                q.append((nr, nc, t + 1))
    return minutes if fresh == 0 else -1

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    edges = [
        [[0]],
        [[1]],
        [[2]],
        [[2, 1, 1], [1, 1, 0], [0, 1, 1]],
        [[2, 1, 1], [0, 1, 1], [1, 0, 1]],
        [[0, 2]],
        [[1, 1, 1], [1, 1, 1]],
        [[2, 2, 2], [2, 1, 2], [2, 2, 2]],
        [[1, 0, 1], [0, 0, 0], [1, 0, 1]],
    ]
    for offset in range(count):
        if offset < len(edges):
            grid = [row[:] for row in edges[offset]]
        else:
            m = rng.randint(1, 10)
            n = rng.randint(1, 10)
            grid = [[rng.choice([0, 0, 1, 1, 2]) for _ in range(n)] for _ in range(m)]
        g2 = [row[:] for row in grid]
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve(g2)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
