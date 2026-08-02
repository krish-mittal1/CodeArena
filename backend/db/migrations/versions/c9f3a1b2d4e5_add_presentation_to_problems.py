"""add_presentation_to_problems

Revision ID: c9f3a1b2d4e5
Revises: b8e2c4f6a1d0
Create Date: 2026-08-03 00:55:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c9f3a1b2d4e5"
down_revision: Union[str, None] = "b8e2c4f6a1d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "problems",
        sa.Column(
            "presentation",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("problems", "presentation")
