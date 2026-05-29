"""Add analysis_mode to vocabulary entries.

Revision ID: 0005_analysis_mode
Revises: 0004_source_type
Create Date: 2026-05-25 00:00:04.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_analysis_mode"
down_revision: str | None = "0004_source_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "vocabulary_entries",
        sa.Column("analysis_mode", sa.String(length=32), nullable=False, server_default="general"),
    )


def downgrade() -> None:
    op.drop_column("vocabulary_entries", "analysis_mode")
