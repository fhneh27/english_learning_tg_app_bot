"""Add persistent suggestion blacklist to users.

Revision ID: 0008_user_suggestion_blacklist
Revises: 0007_media_system
Create Date: 2026-05-26 19:20:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0008_user_suggestion_blacklist"
down_revision: str | None = "0007_media_system"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tg_users",
        sa.Column(
            "suggestion_blacklist",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("tg_users", "suggestion_blacklist")
