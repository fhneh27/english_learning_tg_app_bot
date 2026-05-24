from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import TgUser


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_user(
        self,
        tg_user_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> None:
        insert_statement = insert(TgUser).values(
            tg_user_id=tg_user_id,
            username=username,
            first_name=first_name,
        )

        statement = insert_statement.on_conflict_do_update(
                index_elements=[TgUser.tg_user_id],
                set_={
                    "username": func.coalesce(insert_statement.excluded.username, TgUser.username),
                    "first_name": func.coalesce(insert_statement.excluded.first_name, TgUser.first_name),
                },
            )
        await self.session.execute(statement)

    async def get_by_tg_user_id(self, tg_user_id: int) -> TgUser | None:
        statement = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_users(self, limit: int, offset: int) -> list[TgUser]:
        statement = (
            select(TgUser)
            .order_by(TgUser.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
