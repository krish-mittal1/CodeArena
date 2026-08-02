from __future__ import annotations
import json
import random

def solve(matrix: list[list[int]]) -> list[int]:
    res = []
    while matrix:
        res += matrix.pop(0)
        if matrix and matrix[0]:
            for row in matrix:
                res.append(row.pop())
        if matrix:
            res += matrix.pop()[::-1]
        if matrix and matrix[0]:
            for row in matrix[::-1]:
                res.append(row.pop(0))
    return res


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 6), rng.randint(1, 6)
        matrix = [[rng.randint(-20, 20) for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(matrix),
            "expected_output": json.dumps(solve([row[:] for row in matrix])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
