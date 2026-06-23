from uuid import UUID

from sqlalchemy import Select, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import VocabularyEntry


class VocabularyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entry: VocabularyEntry) -> VocabularyEntry:
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def get_by_id_and_user(self, entry_id: UUID, tg_user_id: int) -> VocabularyEntry | None:
        statement = select(VocabularyEntry).where(
            VocabularyEntry.id == entry_id,
            VocabularyEntry.tg_user_id == tg_user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        tg_user_id: int,
        query: str | None,
        status: str | None,
        source_type: str | None,
        limit: int,
        offset: int,
    ) -> list[VocabularyEntry]:
        statement: Select[tuple[VocabularyEntry]] = (
            select(VocabularyEntry)
            .where(VocabularyEntry.tg_user_id == tg_user_id)
            .order_by(VocabularyEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if query:
            escaped_query = self._escape_ilike(query.strip())
            search_term = f"%{escaped_query}%"
            statement = statement.where(
                or_(
                    VocabularyEntry.original_text.ilike(search_term),
                    VocabularyEntry.translation_ru.ilike(search_term),
                    VocabularyEntry.meaning_ru.ilike(search_term),
                )
            )

        if status:
            statement = statement.where(VocabularyEntry.status == status)

        if source_type:
            statement = statement.where(VocabularyEntry.source_type == source_type)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    def _escape_ilike(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    async def delete_by_id_and_user(self, entry_id: UUID, tg_user_id: int) -> bool:
        statement = delete(VocabularyEntry).where(
            VocabularyEntry.id == entry_id,
            VocabularyEntry.tg_user_id == tg_user_id,
        )
        result = await self.session.execute(statement)
        return bool(result.rowcount)
