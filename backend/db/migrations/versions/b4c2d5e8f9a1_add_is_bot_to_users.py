"""add_is_bot_to_users

Revision ID: b4c2d5e8f9a1
Revises: a3b8d1c2e4f5
Create Date: 2026-03-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c2d5e8f9a1'
down_revision: Union[str, None] = 'a3b8d1c2e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_bot column to users table
    op.add_column('users', sa.Column('is_bot', sa.Boolean(), nullable=False, server_default='false'))
    op.alter_column('users', 'is_bot', server_default=None)


def downgrade() -> None:
    # Remove is_bot column
    op.drop_column('users', 'is_bot')
