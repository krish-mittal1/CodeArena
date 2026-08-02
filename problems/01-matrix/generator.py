from __future__ import annotations
import json
import random
from collections import deque

def solve(mat: list[list[int]]) -> list[list[int]]:
    m, n = len(mat), len(mat[0])
    INF = 10**9
    dist = [[INF] * n for _ in range(m)]
    q = deque()
    for i in range(m):
        for j in range(n):
            if mat[i][j] == 0:
                dist[i][j] = 0
                q.append((i, j))
    while q:
        r, c = q.popleft()
        for nr, nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
            if 0 <= nr < m and 0 <= nc < n and dist[nr][nc] > dist[r][c] + 1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        mat = [[1 if rng.random() < 0.7 else 0 for _ in range(n)] for _ in range(m)]
        if all(all(x == 1 for x in row) for row in mat):
            mat[0][0] = 0
        yield {
            "input": json.dumps(mat),
            "expected_output": json.dumps(solve([row[:] for row in mat])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
