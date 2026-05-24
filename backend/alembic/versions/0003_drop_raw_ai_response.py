"""Drop raw_ai_response from vocabulary entries.

Revision ID: 0003_drop_raw_ai_response
Revises: 0002_users_and_learning_progress
Create Date: 2026-05-24 00:00:02.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_drop_raw_ai_response"
down_revision: str | None = "0002_users_and_learning_progress"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("vocabulary_entries", "raw_ai_response")


def downgrade() -> None:
    op.add_column(
        "vocabulary_entries",
        sa.Column(
            "raw_ai_response",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
