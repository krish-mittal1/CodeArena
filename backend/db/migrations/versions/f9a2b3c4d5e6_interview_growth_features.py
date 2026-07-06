"""interview growth: ai analyses, review queue, practice streaks

Revision ID: f9a2b3c4d5e6
Revises: e8f1a2b3c4d5
Create Date: 2026-07-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f9a2b3c4d5e6"
down_revision: Union[str, None] = "e8f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_title", sa.String(200), nullable=False),
        sa.Column("topic", sa.String(80), nullable=True),
        sa.Column("verdict", sa.String(30), nullable=False),
        sa.Column("analysis", postgresql.JSONB, nullable=False),
        sa.Column("share_slug", sa.String(32), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_ai_analyses_user_created", "ai_analyses", ["user_id", "created_at"])

    op.create_table(
        "review_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_review_queue_user_due", "review_queue", ["user_id", "due_at"])

    op.add_column("users", sa.Column("practice_streak", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("last_practice_date", sa.Date(), nullable=True))
    op.alter_column("users", "practice_streak", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "last_practice_date")
    op.drop_column("users", "practice_streak")
    op.drop_index("idx_review_queue_user_due", table_name="review_queue")
    op.drop_table("review_queue")
    op.drop_index("idx_ai_analyses_user_created", table_name="ai_analyses")
    op.drop_table("ai_analyses")
