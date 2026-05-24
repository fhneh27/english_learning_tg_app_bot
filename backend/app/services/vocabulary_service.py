from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.vocabulary import VocabularyEntry
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import VALID_ENTRY_STATUSES
from app.services.openai_service import OpenAIService


class EntryNotFoundError(Exception):
    """Raised when a user requests a missing vocabulary entry."""


class VocabularyService:
    def __init__(
        self,
        session: AsyncSession,
        repository: VocabularyRepository | None = None,
        user_repository: UserRepository | None = None,
        openai_service: OpenAIService | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or VocabularyRepository(session)
        self.user_repository = user_repository or UserRepository(session)
        self.openai_service = openai_service or OpenAIService()
        self.settings = get_settings()

    async def create_entry(self, tg_user_id: int, text: str) -> VocabularyEntry:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("Text must not be empty.")

        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        analyzed, _ = await self.openai_service.analyze_text(cleaned_text)
        entry = VocabularyEntry(
            tg_user_id=tg_user_id,
            original_text=analyzed.original_text.strip() or cleaned_text,
            normalized_text=analyzed.normalized_text.strip() or cleaned_text.lower(),
            translation_ru=analyzed.translation_ru.strip(),
            meaning_ru=analyzed.meaning_ru.strip(),
            part_of_speech=analyzed.part_of_speech,
            level=analyzed.level,
            transcription=analyzed.transcription,
            examples=[example.model_dump() for example in analyzed.examples],
            synonyms=analyzed.synonyms,
            tags=analyzed.tags,
            status="learning",
            repeat_count=0,
            learned_at=None,
            ai_model=self.settings.openai_model,
        )

        created = await self.repository.create(entry)
        await self.session.commit()
        await self.session.refresh(created)
        return created

    async def list_entries(
        self,
        tg_user_id: int,
        query: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> list[VocabularyEntry]:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        normalized_status = self._validate_status(status) if status else None
        return await self.repository.list_by_user(tg_user_id, query, normalized_status, limit, offset)

    async def get_entry(self, entry_id: UUID, tg_user_id: int) -> VocabularyEntry:
        entry = await self.repository.get_by_id_and_user(entry_id, tg_user_id)
        if entry is None:
            raise EntryNotFoundError("Entry not found.")
        return entry

    async def update_progress(
        self,
        entry_id: UUID,
        tg_user_id: int,
        status: str | None,
        increment_repetition: bool,
    ) -> VocabularyEntry:
        entry = await self.get_entry(entry_id, tg_user_id)

        if increment_repetition:
            entry.repeat_count += 1

        if status is not None:
            next_status = self._validate_status(status)
            entry.status = next_status
            if next_status == "learned":
                entry.learned_at = datetime.now(timezone.utc)
            elif next_status == "learning":
                entry.learned_at = None

        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def delete_entry(self, entry_id: UUID, tg_user_id: int) -> None:
        deleted = await self.repository.delete_by_id_and_user(entry_id, tg_user_id)
        if not deleted:
            raise EntryNotFoundError("Entry not found.")
        await self.session.commit()

    @staticmethod
    def _validate_status(status: str) -> str:
        normalized = status.strip().lower()
        if normalized not in VALID_ENTRY_STATUSES:
            raise ValueError("Status must be one of: new, learning, learned.")
        return normalized
