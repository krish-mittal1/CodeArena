"""nullable submissions.match_id + problem driver columns

Revision ID: a7c4e9f1b2d3
Revises: f9a2b3c4d5e6
Create Date: 2026-07-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a7c4e9f1b2d3"
down_revision: Union[str, None] = "f9a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    )
    return result.first() is not None


def upgrade() -> None:
    # Practice submissions have no match — align DB with the ORM model.
    op.alter_column(
        "submissions",
        "match_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )

    # Recreate FK with ON DELETE CASCADE to match the model.
    op.drop_constraint("submissions_match_id_fkey", "submissions", type_="foreignkey")
    op.create_foreign_key(
        "submissions_match_id_fkey",
        "submissions",
        "matches",
        ["match_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # LeetCode driver metadata used by practice / judge (skip if already present).
    if not _column_exists("problems", "method_name"):
        op.add_column(
            "problems",
            sa.Column("method_name", sa.String(length=200), nullable=True),
        )
    if not _column_exists("problems", "parameters"):
        op.add_column(
            "problems",
            sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )
    if not _column_exists("problems", "return_type"):
        op.add_column(
            "problems",
            sa.Column("return_type", sa.String(length=100), nullable=True),
        )


def downgrade() -> None:
    if _column_exists("problems", "return_type"):
        op.drop_column("problems", "return_type")
    if _column_exists("problems", "parameters"):
        op.drop_column("problems", "parameters")
    if _column_exists("problems", "method_name"):
        op.drop_column("problems", "method_name")

    op.drop_constraint("submissions_match_id_fkey", "submissions", type_="foreignkey")
    op.create_foreign_key(
        "submissions_match_id_fkey",
        "submissions",
        "matches",
        ["match_id"],
        ["id"],
    )

    # Cannot safely re-NOT-NULL if practice rows with NULL match_id exist.
    op.execute("DELETE FROM submissions WHERE match_id IS NULL")
    op.alter_column(
        "submissions",
        "match_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
