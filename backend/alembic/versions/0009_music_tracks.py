"""Add music tracks and vocabulary music source fields.

Revision ID: 0009_music_tracks
Revises: 0008_user_suggestion_blacklist
Create Date: 2026-05-26 20:30:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0009_music_tracks"
down_revision: str | None = "0008_user_suggestion_blacklist"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "music_tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="musicbrainz"),
        sa.Column("provider_track_id", sa.String(length=64), nullable=False),
        sa.Column("provider_release_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("artist_name", sa.Text(), nullable=False),
        sa.Column("release_title", sa.Text(), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("artwork_url", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
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
        sa.UniqueConstraint("tg_user_id", "provider", "provider_track_id", name="uq_music_tracks_user_provider_track"),
    )
    op.create_index("ix_music_tracks_tg_user_id", "music_tracks", ["tg_user_id"], unique=False)
    op.create_index("ix_music_tracks_provider_track_id", "music_tracks", ["provider_track_id"], unique=False)

    op.add_column("vocabulary_entries", sa.Column("music_track_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("vocabulary_entries", sa.Column("source_image_url", sa.Text(), nullable=True))
    op.create_index("ix_vocabulary_entries_music_track_id", "vocabulary_entries", ["music_track_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vocabulary_entries_music_track_id", table_name="vocabulary_entries")
    op.drop_column("vocabulary_entries", "source_image_url")
    op.drop_column("vocabulary_entries", "music_track_id")

    op.drop_index("ix_music_tracks_provider_track_id", table_name="music_tracks")
    op.drop_index("ix_music_tracks_tg_user_id", table_name="music_tracks")
    op.drop_table("music_tracks")
