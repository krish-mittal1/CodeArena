from __future__ import annotations

import json

from backend.problem_bank.upsert import upsert_problem


def encode_lines(*values) -> str:
    return "\n".join(json.dumps(value) for value in values)


def make_case(*inputs, expected_output, idx: int, is_sample: bool = False) -> dict:
    return {
        "input": encode_lines(*inputs),
        "expected_output": json.dumps(expected_output),
        "order_index": idx,
        "is_sample": is_sample,
    }


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    i = 0
    j = 0
    out: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
