from __future__ import annotations
import json
import random

def solve(image: list[list[int]], sr: int, sc: int, color: int) -> list[list[int]]:
    start = image[sr][sc]
    if start == color:
        return image
    m, n = len(image), len(image[0])
    stack = [(sr, sc)]
    image[sr][sc] = color
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and image[nr][nc] == start:
                image[nr][nc] = color
                stack.append((nr, nc))
    return image

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m = rng.randint(1, 12)
        n = rng.randint(1, 12)
        image = [[rng.randint(0, 3) for _ in range(n)] for _ in range(m)]
        sr = rng.randrange(m)
        sc = rng.randrange(n)
        color = rng.randint(0, 5)
        img2 = [row[:] for row in image]
        yield {
            "input": f"{json.dumps(image)}\n{json.dumps(sr)}\n{json.dumps(sc)}\n{json.dumps(color)}",
            "expected_output": json.dumps(solve(img2, sr, sc, color)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
