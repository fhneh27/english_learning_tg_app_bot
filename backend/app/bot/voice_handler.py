import logging
from html import escape

from aiogram import F, Router
from aiogram.types import Message

from app.db.session import AsyncSessionLocal
from app.services.openai_service import OpenAIServiceError
from app.services.voice_intent_service import VoiceIntent, VoiceIntentError, VoiceIntentService
from app.services.voice_media_matcher_service import VoiceMediaMatcherService
from app.services.voice_transcription_service import VoiceTranscriptionError, VoiceTranscriptionService
from app.services.vocabulary_service import VocabularyService

logger = logging.getLogger(__name__)

voice_router = Router()


@voice_router.message(F.voice)
async def process_voice_message(message: Message) -> None:
    if message.from_user is None:
        await message.answer("I could not detect your Telegram account. Please try again.")
        return

    if message.bot is None:
        await message.answer("Something went wrong. Please try again.")
        return

    tg_user_id = message.from_user.id

    # Step 1: transcribe
    transcription_service = VoiceTranscriptionService()
    try:
        transcript = await transcription_service.transcribe(message.bot, message.voice)
    except VoiceTranscriptionError:
        await message.answer(
            "I could not transcribe your voice message. Please try again or type the word manually."
        )
        return

    logger.info("Voice transcript (user=%s): %r", tg_user_id, transcript)

    # Step 2: extract intent
    intent_service = VoiceIntentService()
    try:
        intent = await intent_service.extract(transcript)
    except VoiceIntentError:
        await message.answer(
            "I could not process your voice message right now. Please try again or type the word manually."
        )
        return

    if intent.confidence == "low" or intent.word_or_phrase is None:
        await message.answer(
            "I could not clearly detect the word from your voice message.\n"
            "Please send it again or type the word manually."
        )
        return

    # Step 3: resolve source_type and analysis_mode for the DB
    db_source_type, db_analysis_mode = _map_intent_to_db(intent)

    # Step 4: match media if applicable
    media_item_id = None
    media_season_id = None
    media_episode_id = None
    media_matched = False
    media_source_label = None

    if db_source_type == "media" and intent.media_title:
        async with AsyncSessionLocal() as session:
            matcher = VoiceMediaMatcherService(session)
            result = await matcher.match(
                tg_user_id=tg_user_id,
                media_title=intent.media_title,
                media_type=intent.media_type,
                season_number=intent.season_number,
                episode_number=intent.episode_number,
            )
        if result.found:
            media_item_id = result.media_item_id
            media_season_id = result.media_season_id
            media_episode_id = result.media_episode_id
            media_matched = True
            media_source_label = _build_source_label(
                result.matched_title, intent.season_number, intent.episode_number
            )
        else:
            # Media title mentioned but not in library → save as unsorted, notify user.
            db_source_type = "unsorted"

    elif intent.source_type == "music" and intent.media_title:
        # Music source without MusicBrainz IDs — save as unsorted with a label.
        media_source_label = intent.media_title

    # Step 5: save the word
    async with AsyncSessionLocal() as session:
        vocab_service = VocabularyService(session)
        try:
            entry = await vocab_service.create_entry(
                tg_user_id=tg_user_id,
                text=intent.word_or_phrase,
                source_type=db_source_type,
                analysis_mode=db_analysis_mode,
                media_item_id=media_item_id,
                media_season_id=media_season_id,
                media_episode_id=media_episode_id,
                source_label=media_source_label,
            )
        except ValueError:
            await message.answer("Please send a non-empty English word or phrase.")
            return
        except OpenAIServiceError:
            await message.answer(
                "OpenAI is unavailable right now. Please try again in a moment."
            )
            return
        except Exception:
            logger.exception("Unexpected error saving voice word for user=%s", tg_user_id)
            await message.answer("Something went wrong while saving your word. Please try again.")
            return

    # Step 6: reply
    media_not_found = (
        intent.source_type == "media"
        and intent.media_title
        and not media_matched
    )
    await message.answer(_format_voice_reply(entry, media_source_label, media_not_found))


def _map_intent_to_db(intent: VoiceIntent) -> tuple[str, str]:
    """Map VoiceIntent source_type to the DB source_type and analysis_mode pair."""
    if intent.source_type == "media":
        return "media", "general"
    if intent.source_type == "music":
        return "unsorted", "general"
    if intent.source_type == "slang":
        return "unsorted", "slang"
    return "unsorted", "general"


def _build_source_label(
    title: str | None,
    season_number: int | None,
    episode_number: int | None,
) -> str | None:
    if not title:
        return None
    parts = [title]
    if season_number is not None:
        parts.append(f"S{season_number}")
        if episode_number is not None:
            parts[-1] += f"E{episode_number}"
    return ", ".join(parts)


def _format_voice_reply(entry: object, source_label: str | None, media_not_found: bool) -> str:
    original = escape(getattr(entry, "original_text", ""))
    meaning = escape(getattr(entry, "meaning_ru", ""))
    translation = escape(getattr(entry, "translation_ru", ""))

    lines = [f"<b>{original}</b>  {translation}"]
    lines.append(f"{meaning}")

    if source_label:
        lines.append(f"<i>Source: {escape(source_label)}</i>")

    if media_not_found:
        lines.append(
            "\nWord saved, but I couldn't find the media source in your library. "
            "You can link it manually in the Mini App."
        )
    else:
        lines.append("Saved.")

    return "\n".join(lines)
