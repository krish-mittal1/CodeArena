from __future__ import annotations
import json
import random

def solve(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
    return matrix


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 8)
        matrix = [[rng.randint(-20, 20) for _ in range(n)] for _ in range(n)]
        m2 = [row[:] for row in matrix]
        yield {
            "input": json.dumps(matrix),
            "expected_output": json.dumps(solve(m2)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
