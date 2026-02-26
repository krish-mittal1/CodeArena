"""add_rating_to_problems

Revision ID: a3b8d1c2e4f5
Revises: 7af1a2c69380
Create Date: 2026-02-27 02:42:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = 'a3b8d1c2e4f5'
down_revision: Union[str, None] = '7af1a2c69380'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('problems', sa.Column('rating', sa.Integer(), nullable=False, server_default='800'))


def downgrade() -> None:
    op.drop_column('problems', 'rating')
