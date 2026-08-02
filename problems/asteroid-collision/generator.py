from __future__ import annotations
import json
import random

def solve(asteroids: list[int]) -> list[int]:
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
                continue
            elif stack[-1] == -a:
                stack.pop()
            alive = False
        if alive:
            stack.append(a)
    return stack


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(2, 25)
        asteroids = []
        for _ in range(n):
            v = rng.randint(1, 20)
            asteroids.append(v if rng.random() < 0.5 else -v)
        yield {
            "input": json.dumps(asteroids),
            "expected_output": json.dumps(solve(asteroids)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
