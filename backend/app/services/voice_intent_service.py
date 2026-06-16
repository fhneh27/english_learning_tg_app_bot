import json
import logging

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"

_VALID_SOURCE_TYPES = {"unsorted", "general", "slang", "music", "media"}
_VALID_ANALYSIS_MODES = {"general", "slang"}
_VALID_MEDIA_TYPES = {"movie", "series", "song"}
_VALID_CONFIDENCE = {"high", "low"}

_SYSTEM_PROMPT = """
You extract vocabulary learning intent from a spoken or typed transcript.

The user is learning English vocabulary. They may say something like:
- "I learned the word compose from the series Twilight, season 3, episode 4"
- "What does gring mean in slang?"
- "Add the word shallow from a song"
- "put someone on a map, это фраза из песни Lil Peep veins"
- Just a single word: "compose"

Your job is to detect:
- The English word or phrase the user wants to save.
- The source context (media/music/slang/general).
- Any media or song metadata mentioned.

Rules:
- Return only valid JSON. No Markdown.
- If you cannot clearly identify a word or phrase, set confidence to "low".
- Set confidence to "high" only when the word is clearly stated.
- Normalize word_or_phrase to the base dictionary form (e.g. "composed" → "compose").
- For media_title, extract only the movie/series title, not season or episode numbers.
- For music, fill artist_name and song_title separately (e.g. artist "Lil Peep", song "Veins").
- Input may be Russian, English, or mixed.
- season_number and episode_number must be integers or null.
- source_type values: "media" (movie/series/show), "music" (song/artist/album), "slang" (user explicitly says slang), "general" (no special source), "unsorted" (completely unclear).
- analysis_mode: "slang" if the user asks about slang meaning, otherwise "general".
- media_type: "movie", "series", "song", or null.

Return this exact JSON shape:
{
  "word_or_phrase": "string or null",
  "source_type": "unsorted",
  "analysis_mode": "general",
  "media_title": "string or null",
  "media_type": "string or null",
  "artist_name": "string or null",
  "song_title": "string or null",
  "season_number": null,
  "episode_number": null,
  "confidence": "high or low"
}
""".strip()


class VoiceIntent(BaseModel):
    """Structured intent extracted from a voice transcript."""

    word_or_phrase: str | None = None
    source_type: str = "unsorted"
    analysis_mode: str = "general"
    media_title: str | None = None
    media_type: str | None = None
    artist_name: str | None = None
    song_title: str | None = None
    season_number: int | None = None
    episode_number: int | None = None
    confidence: str = "low"


class VoiceIntentError(Exception):
    """Raised when the intent service itself cannot reach the API or gets a broken response."""


class VoiceIntentService:
    """Extracts vocabulary learning intent from a transcribed voice message."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def extract(self, transcript: str) -> VoiceIntent:
        """Return a VoiceIntent from the transcript.

        Never raises on bad GPT JSON — returns low-confidence instead.
        Raises VoiceIntentError only on API-level failures.
        """
        cleaned = transcript.strip()
        if not cleaned:
            return VoiceIntent(confidence="low")

        raw_data = await self._call_api(cleaned)
        return self._parse_intent(raw_data)

    async def _call_api(self, transcript: str) -> dict:
        payload = {
            "model": self.settings.openai_model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript: {transcript}"},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
                response = await client.post(
                    CHAT_COMPLETIONS_URL,
                    headers={
                        "Authorization": f"Bearer {self.settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Intent API request failed with status %s", exc.response.status_code
            )
            raise VoiceIntentError("Intent extraction API request failed.") from exc
        except httpx.HTTPError as exc:
            logger.exception("Intent API request failed (network error)")
            raise VoiceIntentError("Intent extraction API request failed.") from exc

        try:
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            logger.exception("Intent API returned unexpected response format")
            raise VoiceIntentError("Intent extraction API returned an unexpected format.") from exc

    def _parse_intent(self, data: dict) -> VoiceIntent:
        """Validate and sanitize the GPT response dict into a VoiceIntent.

        Returns a low-confidence result instead of raising on validation failure.
        """
        try:
            intent = VoiceIntent.model_validate(data)
        except ValidationError:
            logger.warning(
                "VoiceIntent validation failed, returning low-confidence result. raw=%s", data
            )
            word = data.get("word_or_phrase") if isinstance(data, dict) else None
            return VoiceIntent(
                word_or_phrase=str(word).strip() if word else None,
                confidence="low",
            )

        # Sanitize enum-like fields to known sets so downstream code can trust them.
        if intent.source_type not in _VALID_SOURCE_TYPES:
            intent.source_type = "unsorted"
        if intent.analysis_mode not in _VALID_ANALYSIS_MODES:
            intent.analysis_mode = "general"
        if intent.media_type not in _VALID_MEDIA_TYPES:
            intent.media_type = None
        if intent.confidence not in _VALID_CONFIDENCE:
            intent.confidence = "low"

        # Blank strings from GPT should be treated as null.
        if intent.word_or_phrase is not None and not intent.word_or_phrase.strip():
            intent.word_or_phrase = None
        if intent.media_title is not None and not intent.media_title.strip():
            intent.media_title = None
        if intent.artist_name is not None and not intent.artist_name.strip():
            intent.artist_name = None
        if intent.song_title is not None and not intent.song_title.strip():
            intent.song_title = None

        if intent.source_type == "music" and intent.song_title is None and intent.media_title:
            intent.song_title = intent.media_title

        # If word is missing after sanitization, force low confidence.
        if intent.word_or_phrase is None:
            intent.confidence = "low"

        logger.info(
            "Voice intent extracted: word=%r source_type=%s confidence=%s",
            intent.word_or_phrase,
            intent.source_type,
            intent.confidence,
        )
        return intent
