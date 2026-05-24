"""Initial vocabulary entries table.

Revision ID: 0001_init_vocabulary_entries
Revises:
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_init_vocabulary_entries"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("translation_ru", sa.Text(), nullable=False),
        sa.Column("meaning_ru", sa.Text(), nullable=False),
        sa.Column("part_of_speech", sa.String(length=64), nullable=True),
        sa.Column("level", sa.String(length=16), nullable=True),
        sa.Column("transcription", sa.Text(), nullable=True),
        sa.Column(
            "examples",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "synonyms",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("ai_model", sa.String(length=128), nullable=True),
        sa.Column(
            "raw_ai_response",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
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
    )
    op.create_index(
        "ix_vocabulary_entries_normalized_text",
        "vocabulary_entries",
        ["normalized_text"],
        unique=False,
    )
    op.create_index(
        "ix_vocabulary_entries_tg_user_id",
        "vocabulary_entries",
        ["tg_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_vocabulary_entries_tg_user_id", table_name="vocabulary_entries")
    op.drop_index("ix_vocabulary_entries_normalized_text", table_name="vocabulary_entries")
    op.drop_table("vocabulary_entries")
