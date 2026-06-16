import logging
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import VocabularyEntry
from app.services.openai_service import OpenAIServiceError
from app.services.voice_intent_service import VoiceIntent, VoiceIntentError, VoiceIntentService
from app.services.voice_media_matcher_service import VoiceMediaMatcherService
from app.services.voice_music_matcher_service import VoiceMusicMatcherService
from app.services.vocabulary_service import VocabularyService

logger = logging.getLogger(__name__)


@dataclass
class WordCaptureResult:
    ok: bool = False
    entry: VocabularyEntry | None = None
    error_message: str | None = None
    source_label: str | None = None
    media_not_found: bool = False
    music_not_found: bool = False
    used_legacy_fallback: bool = False
    intent: VoiceIntent | None = field(default=None, repr=False)


class WordCaptureService:
    """Extract intent from text and save a vocabulary entry with source linking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.intent_service = VoiceIntentService()
        self.media_matcher = VoiceMediaMatcherService(session)
        self.music_matcher = VoiceMusicMatcherService()
        self.vocabulary_service = VocabularyService(session)

    async def capture_and_save(
        self,
        tg_user_id: int,
        raw_text: str,
        *,
        allow_legacy_fallback: bool = False,
    ) -> WordCaptureResult:
        cleaned = raw_text.strip()
        if not cleaned:
            return WordCaptureResult(error_message="Please send a non-empty English word or phrase.")

        try:
            intent = await self.intent_service.extract(cleaned)
        except VoiceIntentError:
            if allow_legacy_fallback:
                return await self._legacy_save(tg_user_id, cleaned)
            return WordCaptureResult(
                error_message=(
                    "I could not process your message right now. Please try again or type the word manually."
                )
            )

        if intent.confidence == "low" or intent.word_or_phrase is None:
            if allow_legacy_fallback:
                return await self._legacy_save(tg_user_id, cleaned)
            return WordCaptureResult(
                error_message=(
                    "I could not clearly detect the word.\n"
                    "Please send it again or type the word manually."
                ),
                intent=intent,
            )

        return await self._save_from_intent(tg_user_id, intent)

    async def _save_from_intent(self, tg_user_id: int, intent: VoiceIntent) -> WordCaptureResult:
        db_source_type, db_analysis_mode = self._map_intent_to_db(intent)
        media_item_id = None
        media_season_id = None
        media_episode_id = None
        media_not_found = False
        music_not_found = False
        source_label = self._build_music_label(intent)

        music_kwargs: dict = {}

        if db_source_type == "media" and intent.media_title:
            media_result = await self.media_matcher.match(
                tg_user_id=tg_user_id,
                media_title=intent.media_title,
                media_type=intent.media_type if intent.media_type in ("movie", "series") else None,
                season_number=intent.season_number,
                episode_number=intent.episode_number,
            )
            if media_result.found:
                media_item_id = media_result.media_item_id
                media_season_id = media_result.media_season_id
                media_episode_id = media_result.media_episode_id
                source_label = self._build_media_label(
                    media_result.matched_title,
                    intent.season_number,
                    intent.episode_number,
                )
            else:
                db_source_type = "unsorted"
                media_not_found = True

        elif self._should_match_music(intent):
            music_result = await self.music_matcher.match(
                artist_name=intent.artist_name,
                song_title=intent.song_title,
                media_title=intent.media_title,
            )
            if music_result.found and music_result.track is not None:
                track = music_result.track
                db_source_type = "music"
                source_label = f"{track.artist_name} - {track.title}"
                music_kwargs = {
                    "music_track_external_id": track.external_id,
                    "music_release_external_id": track.release_external_id,
                    "music_track_title": track.title,
                    "music_artist_name": track.artist_name,
                    "music_release_title": track.release_title,
                    "music_release_year": track.release_year,
                    "music_artwork_url": track.artwork_url,
                    "music_duration_ms": track.duration_ms,
                }
            else:
                db_source_type = "unsorted"
                music_not_found = True

        try:
            entry = await self.vocabulary_service.create_entry(
                tg_user_id=tg_user_id,
                text=intent.word_or_phrase,
                source_type=db_source_type,
                analysis_mode=db_analysis_mode,
                media_item_id=media_item_id,
                media_season_id=media_season_id,
                media_episode_id=media_episode_id,
                source_label=source_label,
                **music_kwargs,
            )
        except ValueError:
            return WordCaptureResult(
                error_message="Please send a non-empty English word or phrase.",
                intent=intent,
            )
        except OpenAIServiceError:
            return WordCaptureResult(
                error_message="OpenAI is unavailable right now. Please try again in a moment.",
                intent=intent,
            )

        return WordCaptureResult(
            ok=True,
            entry=entry,
            source_label=source_label,
            media_not_found=media_not_found,
            music_not_found=music_not_found,
            intent=intent,
        )

    async def _legacy_save(self, tg_user_id: int, text: str) -> WordCaptureResult:
        try:
            entry = await self.vocabulary_service.create_entry(tg_user_id, text)
        except ValueError:
            return WordCaptureResult(error_message="Please send a non-empty English word or phrase.")
        except OpenAIServiceError:
            return WordCaptureResult(
                error_message="OpenAI is unavailable right now. Please try again in a moment."
            )

        return WordCaptureResult(ok=True, entry=entry, used_legacy_fallback=True)

    @staticmethod
    def _should_match_music(intent: VoiceIntent) -> bool:
        if intent.source_type == "music":
            return True
        if intent.media_type == "song":
            return True
        return bool(intent.song_title or intent.artist_name)

    @staticmethod
    def _map_intent_to_db(intent: VoiceIntent) -> tuple[str, str]:
        if intent.source_type == "media":
            return "media", "general"
        if intent.source_type == "music":
            return "music", "general"
        if intent.source_type == "slang":
            return "unsorted", "slang"
        return "unsorted", "general"

    @staticmethod
    def _build_music_label(intent: VoiceIntent) -> str | None:
        artist = (intent.artist_name or "").strip()
        song = (intent.song_title or intent.media_title or "").strip()
        if artist and song:
            return f"{artist} - {song}"
        return song or artist or None

    @staticmethod
    def _build_media_label(
        title: str | None,
        season_number: int | None,
        episode_number: int | None,
    ) -> str | None:
        if not title:
            return None
        if season_number is None:
            return title
        season_part = f"S{season_number}"
        if episode_number is not None:
            season_part += f"E{episode_number}"
        return f"{title}, {season_part}"
