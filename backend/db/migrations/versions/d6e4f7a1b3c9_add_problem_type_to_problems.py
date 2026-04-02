"""add_problem_type_to_problems

Revision ID: d6e4f7a1b3c9
Revises: c5d3e6f9a0b2
Create Date: 2026-04-02 21:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d6e4f7a1b3c9"
down_revision: Union[str, None] = "c5d3e6f9a0b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "problems",
        sa.Column("problem_type", sa.String(length=20), nullable=False, server_default="dsa"),
    )
    op.alter_column("problems", "problem_type", server_default=None)


def downgrade() -> None:
    op.drop_column("problems", "problem_type")
