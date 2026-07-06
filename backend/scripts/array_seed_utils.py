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
