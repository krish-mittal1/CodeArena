"""add onboarding fields to users

Revision ID: e8f1a2b3c4d5
Revises: d6e4f7a1b3c9
Create Date: 2026-07-06 15:45:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8f1a2b3c4d5"
down_revision: Union[str, None] = "d6e4f7a1b3c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("users", sa.Column("preferred_track", sa.String(length=20), nullable=True))
    op.alter_column("users", "onboarding_completed", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "preferred_track")
    op.drop_column("users", "onboarding_completed")
