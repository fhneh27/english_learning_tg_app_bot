"""Add AI custom instructions to users.

Revision ID: 0010_ai_custom_instructions
Revises: 0009_music_tracks
Create Date: 2026-05-29 20:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0010_ai_custom_instructions"
down_revision: str | None = "0009_music_tracks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tg_users", sa.Column("ai_custom_instructions", sa.String(length=2000), nullable=True))


def downgrade() -> None:
    op.drop_column("tg_users", "ai_custom_instructions")
