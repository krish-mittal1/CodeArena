from __future__ import annotations
import json
import random

def solve(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])
    seen = [[False] * n for _ in range(m)]

    def dfs(r: int, c: int) -> None:
        stack = [(r, c)]
        seen[r][c] = True
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == "1" and not seen[nx][ny]:
                    seen[nx][ny] = True
                    stack.append((nx, ny))

    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1" and not seen[i][j]:
                count += 1
                dfs(i, j)
    return count


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    # Crafted edge cases first, then random fill.
    edges = [
        [["0"]],
        [["1"]],
        [["1", "0"], ["0", "1"]],
        [["1", "1"], ["1", "1"]],
        [["0", "0"], ["0", "0"]],
        [["1", "0", "1", "0", "1"]],
        [["1"], ["0"], ["1"], ["0"], ["1"]],
        [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]],
    ]
    for offset in range(count):
        if offset < len(edges):
            grid = edges[offset]
        else:
            m = rng.randint(1, 20)
            n = rng.randint(1, 20)
            dens = rng.choice([0.1, 0.25, 0.35, 0.5, 0.7])
            grid = [["1" if rng.random() < dens else "0" for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve(grid)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
