"""add_is_admin_to_users

Revision ID: c5d3e6f9a0b2
Revises: b4c2d5e8f9a1
Create Date: 2026-03-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d3e6f9a0b2'
down_revision: Union[str, None] = 'b4c2d5e8f9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✓ SECURITY: Add is_admin field to users table for RBAC
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.alter_column('users', 'is_admin', server_default=None)


def downgrade() -> None:
    # Remove is_admin column
    op.drop_column('users', 'is_admin')
