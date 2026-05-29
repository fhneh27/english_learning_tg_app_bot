"""Add source_type to vocabulary entries.

Revision ID: 0004_source_type
Revises: 0003_drop_raw_ai_response
Create Date: 2026-05-25 00:00:03.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_source_type"
down_revision: str | None = "0003_drop_raw_ai_response"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "vocabulary_entries",
        sa.Column("source_type", sa.String(length=32), nullable=False, server_default="unsorted"),
    )


def downgrade() -> None:
    op.drop_column("vocabulary_entries", "source_type")
