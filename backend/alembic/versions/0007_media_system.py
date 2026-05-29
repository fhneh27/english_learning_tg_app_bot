"""Add media system tables and vocabulary media references.

Revision ID: 0007_media_system
Revises: 0006_user_daily_activity
Create Date: 2026-05-25 00:00:06.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007_media_system"
down_revision: str | None = "0006_user_daily_activity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "media_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("media_type", sa.String(length=32), nullable=False),
        sa.Column("tmdb_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("poster_path", sa.Text(), nullable=True),
        sa.Column("backdrop_path", sa.Text(), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("runtime_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("watched_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_watched", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
        sa.UniqueConstraint("tg_user_id", "media_type", "tmdb_id", name="uq_media_items_user_type_tmdb"),
    )
    op.create_index("ix_media_items_tg_user_id", "media_items", ["tg_user_id"], unique=False)
    op.create_index("ix_media_items_media_type", "media_items", ["media_type"], unique=False)

    op.create_table(
        "media_seasons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("series_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tmdb_season_id", sa.Integer(), nullable=True),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("poster_path", sa.Text(), nullable=True),
        sa.Column("episode_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["series_item_id"], ["media_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_item_id", "season_number", name="uq_media_seasons_series_number"),
    )
    op.create_index("ix_media_seasons_series_item_id", "media_seasons", ["series_item_id"], unique=False)

    op.create_table(
        "media_episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("series_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("season_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tmdb_episode_id", sa.Integer(), nullable=True),
        sa.Column("season_number", sa.Integer(), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("runtime_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("watched_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_watched", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
        sa.ForeignKeyConstraint(["series_item_id"], ["media_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["season_id"], ["media_seasons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "episode_number", name="uq_media_episodes_season_episode"),
    )
    op.create_index("ix_media_episodes_series_item_id", "media_episodes", ["series_item_id"], unique=False)
    op.create_index("ix_media_episodes_season_id", "media_episodes", ["season_id"], unique=False)

    op.create_table(
        "media_franchise_movies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("franchise_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("movie_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["franchise_item_id"], ["media_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["movie_item_id"], ["media_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("franchise_item_id", "movie_item_id", name="uq_media_franchise_movie"),
    )
    op.create_index("ix_media_franchise_movies_franchise_item_id", "media_franchise_movies", ["franchise_item_id"], unique=False)
    op.create_index("ix_media_franchise_movies_movie_item_id", "media_franchise_movies", ["movie_item_id"], unique=False)

    op.add_column("vocabulary_entries", sa.Column("media_item_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("vocabulary_entries", sa.Column("media_season_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("vocabulary_entries", sa.Column("media_episode_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("vocabulary_entries", sa.Column("media_franchise_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("vocabulary_entries", sa.Column("source_label", sa.String(length=256), nullable=True))
    op.create_index("ix_vocabulary_entries_media_item_id", "vocabulary_entries", ["media_item_id"], unique=False)
    op.create_index("ix_vocabulary_entries_media_season_id", "vocabulary_entries", ["media_season_id"], unique=False)
    op.create_index("ix_vocabulary_entries_media_episode_id", "vocabulary_entries", ["media_episode_id"], unique=False)
    op.create_index("ix_vocabulary_entries_media_franchise_id", "vocabulary_entries", ["media_franchise_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vocabulary_entries_media_franchise_id", table_name="vocabulary_entries")
    op.drop_index("ix_vocabulary_entries_media_episode_id", table_name="vocabulary_entries")
    op.drop_index("ix_vocabulary_entries_media_season_id", table_name="vocabulary_entries")
    op.drop_index("ix_vocabulary_entries_media_item_id", table_name="vocabulary_entries")
    op.drop_column("vocabulary_entries", "source_label")
    op.drop_column("vocabulary_entries", "media_franchise_id")
    op.drop_column("vocabulary_entries", "media_episode_id")
    op.drop_column("vocabulary_entries", "media_season_id")
    op.drop_column("vocabulary_entries", "media_item_id")

    op.drop_index("ix_media_franchise_movies_movie_item_id", table_name="media_franchise_movies")
    op.drop_index("ix_media_franchise_movies_franchise_item_id", table_name="media_franchise_movies")
    op.drop_table("media_franchise_movies")

    op.drop_index("ix_media_episodes_season_id", table_name="media_episodes")
    op.drop_index("ix_media_episodes_series_item_id", table_name="media_episodes")
    op.drop_table("media_episodes")

    op.drop_index("ix_media_seasons_series_item_id", table_name="media_seasons")
    op.drop_table("media_seasons")

    op.drop_index("ix_media_items_media_type", table_name="media_items")
    op.drop_index("ix_media_items_tg_user_id", table_name="media_items")
    op.drop_table("media_items")
