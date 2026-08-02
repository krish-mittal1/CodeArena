from __future__ import annotations
import json
import random

def solve(board: list[str]) -> bool:
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            ch = board[i][j]
            if ch == ".":
                continue
            b = (i // 3) * 3 + j // 3
            if ch in rows[i] or ch in cols[j] or ch in boxes[b]:
                return False
            rows[i].add(ch)
            cols[j].add(ch)
            boxes[b].add(ch)
    return True


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        board = [["."] * 9 for _ in range(9)]
        # place a few digits without conflict when possible
        for _ in range(rng.randint(0, 15)):
            i, j = rng.randint(0, 8), rng.randint(0, 8)
            d = str(rng.randint(1, 9))
            board[i][j] = d
        # occasionally force conflict
        if rng.random() < 0.3:
            board[0][0] = board[0][1] = "5"
        rows = ["".join(r) for r in board]
        yield {
            "input": json.dumps(rows),
            "expected_output": json.dumps(solve(rows)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
