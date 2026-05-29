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

    async def get_suggestion_blacklist(self, tg_user_id: int) -> list[str]:
        user = await self.get_by_tg_user_id(tg_user_id)
        if user is None:
            return []
        return self._normalize_blacklist(user.suggestion_blacklist)

    async def add_to_suggestion_blacklist(self, tg_user_id: int, text: str) -> list[str]:
        normalized_text = self._normalize_blacklist_text(text)
        if not normalized_text:
            return await self.get_suggestion_blacklist(tg_user_id)

        user = await self.get_by_tg_user_id(tg_user_id)
        if user is None:
            await self.upsert_user(tg_user_id=tg_user_id)
            user = await self.get_by_tg_user_id(tg_user_id)
        if user is None:
            return []

        next_blacklist = self._normalize_blacklist([*user.suggestion_blacklist, normalized_text])
        user.suggestion_blacklist = next_blacklist
        self.session.add(user)
        return next_blacklist

    @staticmethod
    def _normalize_blacklist_text(text: str) -> str:
        return " ".join(text.strip().lower().split())

    @classmethod
    def _normalize_blacklist(cls, items: list[str] | None) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in items or []:
            value = cls._normalize_blacklist_text(item)
            if value and value not in seen:
                seen.add(value)
                normalized.append(value)
        return normalized
