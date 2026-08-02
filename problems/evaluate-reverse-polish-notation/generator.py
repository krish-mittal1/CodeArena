from __future__ import annotations
import json
import random

def solve(tokens: list[str]) -> int:
    stack = []
    for t in tokens:
        if t in "+-*/":
            b, a = stack.pop(), stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(t))
    return stack[0]


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        # Build a simple expression tree as RPN: a op b, nested
        a, b = rng.randint(-20, 20), rng.randint(1, 20)
        op = rng.choice(["+", "-", "*", "/"])
        tokens = [str(a), str(b), op]
        c = rng.randint(-10, 10)
        tokens = tokens + [str(c), rng.choice(["+", "-"])]
        yield {
            "input": json.dumps(tokens),
            "expected_output": json.dumps(solve(tokens)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
