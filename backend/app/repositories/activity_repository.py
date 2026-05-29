from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.streak import UserDailyActivity


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def mark_daily_activity(
        self,
        tg_user_id: int,
        activity_date: date,
        activity_kind: str,
    ) -> None:
        insert_statement = insert(UserDailyActivity).values(
            tg_user_id=tg_user_id,
            activity_date=activity_date,
            action_count=1,
            last_activity_kind=activity_kind,
        )
        statement = insert_statement.on_conflict_do_update(
            index_elements=[UserDailyActivity.tg_user_id, UserDailyActivity.activity_date],
            set_={
                "action_count": UserDailyActivity.action_count + 1,
                "last_activity_kind": insert_statement.excluded.last_activity_kind,
            },
        )
        await self.session.execute(statement)

    async def list_by_user(self, tg_user_id: int) -> list[UserDailyActivity]:
        statement: Select[tuple[UserDailyActivity]] = (
            select(UserDailyActivity)
            .where(UserDailyActivity.tg_user_id == tg_user_id)
            .order_by(UserDailyActivity.activity_date.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
