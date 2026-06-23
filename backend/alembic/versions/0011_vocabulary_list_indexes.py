"""Add composite indexes for vocabulary list queries.

Revision ID: 0011_vocabulary_list_indexes
Revises: 0010_ai_custom_instructions
Create Date: 2026-06-23 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011_vocabulary_list_indexes"
down_revision: str | None = "0010_ai_custom_instructions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_vocabulary_entries_user_created",
        "vocabulary_entries",
        ["tg_user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_vocabulary_entries_user_status",
        "vocabulary_entries",
        ["tg_user_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_vocabulary_entries_user_status", table_name="vocabulary_entries")
    op.drop_index("ix_vocabulary_entries_user_created", table_name="vocabulary_entries")
