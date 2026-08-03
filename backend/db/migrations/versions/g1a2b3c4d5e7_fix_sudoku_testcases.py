"""fix valid sudoku test cases expected output

Revision ID: g1a2b3c4d5e7
Revises: f9a2b3c4d5e6
Create Date: 2026-08-03
"""

import json
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "g1a2b3c4d5e7"
down_revision: Union[str, None] = "c9f3a1b2d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_valid_sudoku(raw_input: str) -> bool:
    try:
        data = json.loads(raw_input)
    except Exception:
        data = [line.strip().strip('"') for line in raw_input.strip().split("\n") if line.strip()]

    if isinstance(data, str):
        data = json.loads(data)

    if not isinstance(data, list) or len(data) != 9:
        return False

    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]

    for i in range(9):
        row_str = data[i]
        if not isinstance(row_str, str) or len(row_str) != 9:
            return False
        for j in range(9):
            ch = row_str[j]
            if ch == ".":
                continue
            if not ch.isdigit() or ch == "0":
                return False
            box_idx = (i // 3) * 3 + (j // 3)
            if ch in rows[i] or ch in cols[j] or ch in boxes[box_idx]:
                return False
            rows[i].add(ch)
            cols[j].add(ch)
            boxes[box_idx].add(ch)
    return True


def upgrade() -> None:
    conn = op.get_bind()
    prob = conn.execute(
        sa.text("SELECT id FROM problems WHERE title = 'Valid Sudoku' OR slug = 'valid-sudoku'")
    ).fetchone()

    if not prob:
        return

    problem_id = prob[0]
    tcs = conn.execute(
        sa.text("SELECT id, input, expected_output FROM test_cases WHERE problem_id = :pid"),
        {"pid": problem_id},
    ).fetchall()

    for tc_id, tc_input, tc_expected in tcs:
        correct_val = _is_valid_sudoku(tc_input)
        correct_str = "true" if correct_val else "false"
        if str(tc_expected).strip().lower() != correct_str:
            conn.execute(
                sa.text("UPDATE test_cases SET expected_output = :exp WHERE id = :id"),
                {"exp": correct_str, "id": tc_id},
            )


def downgrade() -> None:
    pass
