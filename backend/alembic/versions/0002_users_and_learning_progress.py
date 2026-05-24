"""Add tg_users and learning progress fields.

Revision ID: 0002_users_and_learning_progress
Revises: 0001_init_vocabulary_entries
Create Date: 2026-05-24 00:00:01.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_users_and_learning_progress"
down_revision: str | None = "0001_init_vocabulary_entries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tg_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tg_user_id", name="uq_tg_users_tg_user_id"),
    )
    op.create_index("ix_tg_users_tg_user_id", "tg_users", ["tg_user_id"], unique=False)

    op.add_column(
        "vocabulary_entries",
        sa.Column("repeat_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "vocabulary_entries",
        sa.Column("learned_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("vocabulary_entries", "status", server_default="learning")

    op.execute(
        "UPDATE vocabulary_entries SET status = 'learning' WHERE status = 'new'"
    )


def downgrade() -> None:
    op.alter_column("vocabulary_entries", "status", server_default="new")
    op.drop_column("vocabulary_entries", "learned_at")
    op.drop_column("vocabulary_entries", "repeat_count")

    op.drop_index("ix_tg_users_tg_user_id", table_name="tg_users")
    op.drop_table("tg_users")
