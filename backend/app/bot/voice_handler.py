import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from app.bot.entry_replies import format_capture_reply
from app.db.session import AsyncSessionLocal
from app.services.voice_transcription_service import VoiceTranscriptionError, VoiceTranscriptionService
from app.services.word_capture_service import WordCaptureService

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
    logger.info("Voice message received from user=%s", tg_user_id)

    await message.answer("Processing your voice message...")
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        transcription_service = VoiceTranscriptionService()
        transcript = await transcription_service.transcribe(message.bot, message.voice)
        logger.info("Voice transcript (user=%s): %r", tg_user_id, transcript)

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        async with AsyncSessionLocal() as session:
            capture_service = WordCaptureService(session)
            result = await capture_service.capture_and_save(
                tg_user_id,
                transcript,
                allow_legacy_fallback=False,
            )

        await message.answer(format_capture_reply(result))
    except VoiceTranscriptionError:
        await message.answer(
            "I could not transcribe your voice message. Please try again or type the word manually."
        )
    except Exception:
        logger.exception("Unexpected error while processing voice message for user=%s", tg_user_id)
        await message.answer("Something went wrong while processing your voice message. Please try again.")


@voice_router.message(F.audio)
async def process_audio_file(message: Message) -> None:
    await message.answer(
        "Please send a voice message using the microphone button, not an audio file attachment."
    )
