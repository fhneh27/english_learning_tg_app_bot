from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.music import MusicTrack
from app.models.vocabulary import VocabularyEntry
from app.repositories.activity_repository import ActivityRepository
from app.repositories.music_repository import MusicRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.schemas.vocabulary import AIVocabularyPayload, VALID_ENTRY_STATUSES, VALID_SOURCE_TYPES
from app.schemas.vocabulary import VALID_ANALYSIS_MODES, VocabularyFollowUpResponse
from app.services.openai_service import OpenAIService
from app.services.streak_service import StreakService


class EntryNotFoundError(Exception):
    """Raised when a user requests a missing vocabulary entry."""


class VocabularyService:
    def __init__(
        self,
        session: AsyncSession,
        repository: VocabularyRepository | None = None,
        music_repository: MusicRepository | None = None,
        user_repository: UserRepository | None = None,
        activity_repository: ActivityRepository | None = None,
        openai_service: OpenAIService | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or VocabularyRepository(session)
        self.music_repository = music_repository or MusicRepository(session)
        self.user_repository = user_repository or UserRepository(session)
        self.activity_repository = activity_repository or ActivityRepository(session)
        self.openai_service = openai_service or OpenAIService()
        self.streak_service = StreakService(self.session, self.activity_repository, self.user_repository)
        self.settings = get_settings()

    async def create_entry(
        self,
        tg_user_id: int,
        text: str,
        source_type: str = "unsorted",
        analysis_mode: str = "general",
        media_item_id: UUID | None = None,
        media_season_id: UUID | None = None,
        media_episode_id: UUID | None = None,
        media_franchise_id: UUID | None = None,
        music_track_external_id: str | None = None,
        music_release_external_id: str | None = None,
        music_track_title: str | None = None,
        music_artist_name: str | None = None,
        music_release_title: str | None = None,
        music_release_year: int | None = None,
        music_artwork_url: str | None = None,
        music_duration_ms: int | None = None,
        source_label: str | None = None,
    ) -> VocabularyEntry:
        analyzed, _ = await self.analyze_text(text, analysis_mode, tg_user_id)
        return await self.save_entry(
            tg_user_id=tg_user_id,
            analyzed=analyzed,
            source_type=source_type,
            analysis_mode=analysis_mode,
            media_item_id=media_item_id,
            media_season_id=media_season_id,
            media_episode_id=media_episode_id,
            media_franchise_id=media_franchise_id,
            music_track_external_id=music_track_external_id,
            music_release_external_id=music_release_external_id,
            music_track_title=music_track_title,
            music_artist_name=music_artist_name,
            music_release_title=music_release_title,
            music_release_year=music_release_year,
            music_artwork_url=music_artwork_url,
            music_duration_ms=music_duration_ms,
            source_label=source_label,
        )

    async def analyze_text(
        self,
        text: str,
        analysis_mode: str = "general",
        tg_user_id: int | None = None,
    ) -> tuple[AIVocabularyPayload, str | None]:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("Text must not be empty.")

        custom_instructions = None
        if tg_user_id:
            user = await self.user_repository.get_by_tg_user_id(tg_user_id)
            if user:
                custom_instructions = user.ai_custom_instructions

        normalized_mode = self._validate_analysis_mode(analysis_mode)
        analyzed, _ = await self.openai_service.analyze_text(cleaned_text, normalized_mode, custom_instructions)
        return analyzed, self.settings.openai_model

    async def save_entry(
        self,
        tg_user_id: int,
        analyzed: AIVocabularyPayload,
        source_type: str = "unsorted",
        analysis_mode: str = "general",
        media_item_id: UUID | None = None,
        media_season_id: UUID | None = None,
        media_episode_id: UUID | None = None,
        media_franchise_id: UUID | None = None,
        music_track_external_id: str | None = None,
        music_release_external_id: str | None = None,
        music_track_title: str | None = None,
        music_artist_name: str | None = None,
        music_release_title: str | None = None,
        music_release_year: int | None = None,
        music_artwork_url: str | None = None,
        music_duration_ms: int | None = None,
        source_label: str | None = None,
    ) -> VocabularyEntry:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        original_text = analyzed.original_text.strip()
        normalized_text = analyzed.normalized_text.strip()

        if not original_text:
            raise ValueError("Analyzed text must include original_text.")
        if not normalized_text:
            normalized_text = original_text.lower()

        normalized_source_type = self._validate_source_type(source_type)
        attach_media = normalized_source_type == "media"
        attach_music = normalized_source_type == "music"
        music_track = await self._resolve_music_track(
            tg_user_id=tg_user_id,
            attach_music=attach_music,
            music_track_external_id=music_track_external_id,
            music_release_external_id=music_release_external_id,
            music_track_title=music_track_title,
            music_artist_name=music_artist_name,
            music_release_title=music_release_title,
            music_release_year=music_release_year,
            music_artwork_url=music_artwork_url,
            music_duration_ms=music_duration_ms,
        )
        resolved_source_label = source_label.strip() if source_label else None
        if attach_music and music_track is not None:
            resolved_source_label = f"{music_track.artist_name} - {music_track.title}"

        entry = VocabularyEntry(
            tg_user_id=tg_user_id,
            original_text=original_text,
            normalized_text=normalized_text,
            translation_ru=analyzed.translation_ru.strip(),
            meaning_ru=analyzed.meaning_ru.strip(),
            part_of_speech=analyzed.part_of_speech,
            level=analyzed.level,
            transcription=analyzed.transcription,
            examples=[example.model_dump() for example in analyzed.examples],
            synonyms=analyzed.synonyms,
            tags=analyzed.tags,
            status="learning",
            source_type=normalized_source_type,
            analysis_mode=self._validate_analysis_mode(analysis_mode),
            media_item_id=media_item_id if attach_media else None,
            media_season_id=media_season_id if attach_media else None,
            media_episode_id=media_episode_id if attach_media else None,
            media_franchise_id=media_franchise_id if attach_media else None,
            music_track_id=music_track.id if attach_music and music_track else None,
            source_label=resolved_source_label if (attach_media or attach_music) else None,
            source_image_url=music_track.artwork_url if attach_music and music_track else None,
            repeat_count=0,
            learned_at=None,
            ai_model=self.settings.openai_model,
        )

        created = await self.repository.create(entry)
        await self.streak_service.record_activity(tg_user_id, "save_word")
        await self.session.commit()
        await self.session.refresh(created)
        return created

    async def list_entries(
        self,
        tg_user_id: int,
        query: str | None,
        status: str | None,
        source_type: str | None,
        limit: int,
        offset: int,
    ) -> list[VocabularyEntry]:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        normalized_status = self._validate_status(status) if status else None
        normalized_source_type = self._validate_source_type(source_type) if source_type else None
        return await self.repository.list_by_user(
            tg_user_id,
            query,
            normalized_status,
            normalized_source_type,
            limit,
            offset,
        )

    async def get_entry(self, entry_id: UUID, tg_user_id: int) -> VocabularyEntry:
        entry = await self.repository.get_by_id_and_user(entry_id, tg_user_id)
        if entry is None:
            raise EntryNotFoundError("Entry not found.")
        return entry

    async def explain_entry(
        self,
        entry_id: UUID,
        tg_user_id: int,
        prompt: str,
    ) -> VocabularyFollowUpResponse:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            raise ValueError("Prompt must not be empty.")

        custom_instructions = None
        user = await self.user_repository.get_by_tg_user_id(tg_user_id)
        if user:
            custom_instructions = user.ai_custom_instructions

        entry = await self.get_entry(entry_id, tg_user_id)
        follow_up, _ = await self.openai_service.explain_entry(entry, cleaned_prompt, custom_instructions)
        if follow_up.follow_up_model is None:
            follow_up.follow_up_model = self.settings.openai_model
        await self.streak_service.record_activity(tg_user_id, "ask_ai")
        await self.session.commit()
        return follow_up

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

        await self.streak_service.record_activity(tg_user_id, "review_word")
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

    @staticmethod
    def _validate_source_type(source_type: str) -> str:
        normalized = source_type.strip().lower()
        if normalized not in VALID_SOURCE_TYPES:
            raise ValueError("Source type must be one of: unsorted, media, music.")
        return normalized

    @staticmethod
    def _validate_analysis_mode(analysis_mode: str) -> str:
        normalized = analysis_mode.strip().lower()
        if normalized not in VALID_ANALYSIS_MODES:
            raise ValueError("Analysis mode must be one of: general, slang, conversation.")
        return normalized

    async def _resolve_music_track(
        self,
        *,
        tg_user_id: int,
        attach_music: bool,
        music_track_external_id: str | None,
        music_release_external_id: str | None,
        music_track_title: str | None,
        music_artist_name: str | None,
        music_release_title: str | None,
        music_release_year: int | None,
        music_artwork_url: str | None,
        music_duration_ms: int | None,
    ) -> MusicTrack | None:
        if not attach_music:
            return None

        provider_track_id = (music_track_external_id or "").strip()
        title = (music_track_title or "").strip()
        artist_name = (music_artist_name or "").strip()

        if not provider_track_id or not title or not artist_name:
            raise ValueError("Select a music track before saving this word to Music.")

        return await self.music_repository.upsert_track(
            tg_user_id=tg_user_id,
            provider="musicbrainz",
            provider_track_id=provider_track_id,
            provider_release_id=(music_release_external_id or "").strip() or None,
            title=title,
            artist_name=artist_name,
            release_title=(music_release_title or "").strip() or None,
            release_year=music_release_year,
            artwork_url=(music_artwork_url or "").strip() or None,
            duration_ms=music_duration_ms,
        )
