from __future__ import annotations
import json
import random

def solve(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    r, c = 0, n - 1
    while r < m and c >= 0:
        if matrix[r][c] == target:
            return True
        if matrix[r][c] > target:
            c -= 1
        else:
            r += 1
    return False


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        vals = sorted(rng.sample(range(-50, 100), m * n))
        matrix = [vals[i*n:(i+1)*n] for i in range(m)]
        # enforce column sorted by regenerating carefully
        matrix = []
        base = [rng.randint(-20, 20) for _ in range(n)]
        base.sort()
        prev = base
        matrix.append(prev[:])
        for _ in range(m - 1):
            row = [prev[j] + rng.randint(0, 5) for j in range(n)]
            for j in range(1, n):
                row[j] = max(row[j], row[j-1] + 1)
            matrix.append(row)
            prev = row
        target = rng.randint(-30, 80)
        yield {
            "input": f"{json.dumps(matrix)}\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(matrix, target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
