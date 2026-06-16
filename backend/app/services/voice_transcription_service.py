import io
import logging

import httpx
from aiogram import Bot
from aiogram.types import Voice

from app.core.config import get_settings

logger = logging.getLogger(__name__)

TRANSCRIPTION_API_URL = "https://api.openai.com/v1/audio/transcriptions"


class VoiceTranscriptionError(Exception):
    """Raised when voice transcription fails or returns an empty result."""


class VoiceTranscriptionService:
    """Downloads a Telegram voice message and transcribes it via the OpenAI audio API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def transcribe(self, bot: Bot, voice: Voice) -> str:
        """Download the voice file and return the transcribed text.

        Raises VoiceTranscriptionError on download failure, API error, or empty result.
        """
        audio_buffer = await self._download_voice(bot, voice)
        return await self._call_transcription_api(audio_buffer)

    async def _download_voice(self, bot: Bot, voice: Voice) -> io.BytesIO:
        """Fetch the OGG voice file from Telegram into an in-memory buffer."""
        buffer = io.BytesIO()
        try:
            downloaded = await bot.download(voice.file_id, destination=buffer)
            if downloaded is not None and downloaded is not buffer:
                buffer = downloaded
        except Exception as exc:
            logger.exception("Failed to download voice file (file_id=%s)", voice.file_id)
            raise VoiceTranscriptionError("Could not download the voice message.") from exc

        buffer.seek(0)
        if buffer.getbuffer().nbytes == 0:
            raise VoiceTranscriptionError("Downloaded voice file is empty.")
        return buffer

    async def _call_transcription_api(self, audio_buffer: io.BytesIO) -> str:
        """POST the audio buffer to the transcription endpoint and return the transcript."""
        try:
            async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
                response = await client.post(
                    TRANSCRIPTION_API_URL,
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    files={"file": ("voice.ogg", audio_buffer, "audio/ogg")},
                    data={"model": self.settings.openai_transcription_model},
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Transcription API returned status %s", exc.response.status_code
            )
            raise VoiceTranscriptionError("Transcription API request failed.") from exc
        except httpx.HTTPError as exc:
            logger.exception("Transcription API request failed (network error)")
            raise VoiceTranscriptionError("Transcription API request failed.") from exc

        transcript = response.json().get("text", "").strip()
        if not transcript:
            raise VoiceTranscriptionError("Transcription returned an empty result.")
        logger.info("Voice transcribed successfully (%d chars)", len(transcript))
        return transcript
