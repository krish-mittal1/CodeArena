"""add match_problems for multi-problem battles

Revision ID: b8e2c4f6a1d0
Revises: a7c4e9f1b2d3
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b8e2c4f6a1d0"
down_revision: Union[str, None] = "a7c4e9f1b2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_problems",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "order_index", name="uq_match_problems_order"),
        sa.UniqueConstraint("match_id", "problem_id", name="uq_match_problems_problem"),
    )
    op.create_index("idx_match_problems_match_id", "match_problems", ["match_id"])

    # Backfill existing matches: single problem_id becomes order_index 0
    # gen_random_uuid() is built-in on PostgreSQL 13+
    op.execute(
        sa.text(
            """
            INSERT INTO match_problems (id, match_id, problem_id, order_index)
            SELECT gen_random_uuid(), m.id, m.problem_id, 0
            FROM matches m
            WHERE NOT EXISTS (
                SELECT 1 FROM match_problems mp WHERE mp.match_id = m.id
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index("idx_match_problems_match_id", table_name="match_problems")
    op.drop_table("match_problems")
