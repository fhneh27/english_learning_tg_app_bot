"""Add user daily activity for streak tracking.

Revision ID: 0006_user_daily_activity
Revises: 0005_analysis_mode
Create Date: 2026-05-25 00:00:05.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_user_daily_activity"
down_revision: str | None = "0005_analysis_mode"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_daily_activity",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("action_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_activity_kind", sa.String(length=32), nullable=False, server_default="practice"),
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
        sa.UniqueConstraint("tg_user_id", "activity_date", name="uq_user_daily_activity_user_date"),
    )
    op.create_index("ix_user_daily_activity_tg_user_id", "user_daily_activity", ["tg_user_id"], unique=False)
    op.create_index("ix_user_daily_activity_activity_date", "user_daily_activity", ["activity_date"], unique=False)

    op.execute(
        """
        INSERT INTO user_daily_activity (id, tg_user_id, activity_date, action_count, last_activity_kind)
        SELECT md5(random()::text || clock_timestamp()::text || source.tg_user_id::text || source.activity_date::text)::uuid,
               source.tg_user_id,
               source.activity_date,
               1,
               'backfill'
        FROM (
            SELECT DISTINCT tg_user_id, created_at::date AS activity_date
            FROM vocabulary_entries
            WHERE created_at IS NOT NULL
            UNION
            SELECT DISTINCT tg_user_id, learned_at::date AS activity_date
            FROM vocabulary_entries
            WHERE learned_at IS NOT NULL
        ) AS source
        """
    )


def downgrade() -> None:
    op.drop_index("ix_user_daily_activity_activity_date", table_name="user_daily_activity")
    op.drop_index("ix_user_daily_activity_tg_user_id", table_name="user_daily_activity")
    op.drop_table("user_daily_activity")
