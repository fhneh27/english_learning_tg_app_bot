"""
Unit tests for VoiceIntentService._parse_intent and VoiceIntentService.extract.

These tests cover the parsing and sanitization logic.
No real HTTP calls are made — _call_api is mocked.

Run with:
    pip install pytest pytest-asyncio
    pytest backend/tests/test_voice_intent_service.py -v
"""

import sys
import os
from unittest.mock import AsyncMock, patch

import pytest

# Allow running from the backend/ directory or the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.voice_intent_service import (  # noqa: E402
    VoiceIntent,
    VoiceIntentError,
    VoiceIntentService,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_service() -> VoiceIntentService:
    """Return a VoiceIntentService without loading real settings."""
    with patch("app.services.voice_intent_service.get_settings"):
        return VoiceIntentService()


# ---------------------------------------------------------------------------
# _parse_intent — synchronous, no mocking needed
# ---------------------------------------------------------------------------


class TestParseIntent:
    def setup_method(self):
        self.service = make_service()

    def test_valid_high_confidence_media(self):
        data = {
            "word_or_phrase": "compose",
            "source_type": "media",
            "analysis_mode": "general",
            "media_title": "Twilight",
            "media_type": "series",
            "season_number": 3,
            "episode_number": 4,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.word_or_phrase == "compose"
        assert intent.source_type == "media"
        assert intent.analysis_mode == "general"
        assert intent.media_title == "Twilight"
        assert intent.media_type == "series"
        assert intent.season_number == 3
        assert intent.episode_number == 4
        assert intent.confidence == "high"

    def test_valid_slang_response(self):
        data = {
            "word_or_phrase": "gring",
            "source_type": "slang",
            "analysis_mode": "slang",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.word_or_phrase == "gring"
        assert intent.source_type == "slang"
        assert intent.analysis_mode == "slang"
        assert intent.confidence == "high"

    def test_valid_music_response(self):
        data = {
            "word_or_phrase": "shallow",
            "source_type": "music",
            "analysis_mode": "general",
            "media_title": "A Star Is Born",
            "media_type": "song",
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.word_or_phrase == "shallow"
        assert intent.source_type == "music"
        assert intent.media_title == "A Star Is Born"
        assert intent.media_type == "song"
        assert intent.song_title == "A Star Is Born"
        assert intent.confidence == "high"

    def test_music_media_title_copied_to_song_title(self):
        data = {
            "word_or_phrase": "veins",
            "source_type": "music",
            "analysis_mode": "general",
            "media_title": "Veins",
            "media_type": "song",
            "artist_name": "Lil Peep",
            "song_title": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.song_title == "Veins"
        assert intent.artist_name == "Lil Peep"

    def test_invalid_source_type_clamped_to_unsorted(self):
        data = {
            "word_or_phrase": "test",
            "source_type": "unknown_garbage",
            "analysis_mode": "general",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.source_type == "unsorted"
        assert intent.confidence == "high"

    def test_invalid_analysis_mode_clamped_to_general(self):
        data = {
            "word_or_phrase": "hello",
            "source_type": "general",
            "analysis_mode": "formal",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.analysis_mode == "general"

    def test_invalid_media_type_clamped_to_none(self):
        data = {
            "word_or_phrase": "test",
            "source_type": "media",
            "analysis_mode": "general",
            "media_title": "Something",
            "media_type": "podcast",
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.media_type is None

    def test_invalid_confidence_clamped_to_low(self):
        data = {
            "word_or_phrase": "test",
            "source_type": "general",
            "analysis_mode": "general",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "medium",
        }
        intent = self.service._parse_intent(data)

        assert intent.confidence == "low"

    def test_blank_word_forces_low_confidence(self):
        data = {
            "word_or_phrase": "   ",
            "source_type": "general",
            "analysis_mode": "general",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.word_or_phrase is None
        assert intent.confidence == "low"

    def test_blank_media_title_becomes_none(self):
        data = {
            "word_or_phrase": "compose",
            "source_type": "media",
            "analysis_mode": "general",
            "media_title": "  ",
            "media_type": "series",
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        intent = self.service._parse_intent(data)

        assert intent.media_title is None

    def test_validation_failure_returns_low_confidence_with_word(self):
        """Pydantic validation fails (e.g. wrong type) — should not raise."""
        data = {
            "word_or_phrase": "compose",
            "season_number": "not-an-int",  # wrong type — triggers ValidationError
        }
        intent = self.service._parse_intent(data)

        assert intent.confidence == "low"
        assert intent.word_or_phrase == "compose"

    def test_completely_empty_dict_returns_low_confidence(self):
        intent = self.service._parse_intent({})

        assert intent.confidence == "low"
        assert intent.word_or_phrase is None

    def test_non_dict_returns_low_confidence(self):
        intent = self.service._parse_intent("not a dict")  # type: ignore[arg-type]

        assert intent.confidence == "low"
        assert intent.word_or_phrase is None


# ---------------------------------------------------------------------------
# extract() — async, _call_api mocked
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestExtract:
    def setup_method(self):
        self.service = make_service()

    async def test_empty_transcript_returns_low_confidence_without_api_call(self):
        with patch.object(self.service, "_call_api", new_callable=AsyncMock) as mock_api:
            intent = await self.service.extract("   ")

        mock_api.assert_not_called()
        assert intent.confidence == "low"
        assert intent.word_or_phrase is None

    async def test_successful_extraction(self):
        api_response = {
            "word_or_phrase": "compose",
            "source_type": "media",
            "analysis_mode": "general",
            "media_title": "Twilight",
            "media_type": "series",
            "season_number": 3,
            "episode_number": 4,
            "confidence": "high",
        }
        with patch.object(self.service, "_call_api", new_callable=AsyncMock, return_value=api_response):
            intent = await self.service.extract("I learned compose from Twilight season 3")

        assert intent.word_or_phrase == "compose"
        assert intent.confidence == "high"
        assert intent.media_title == "Twilight"
        assert intent.season_number == 3

    async def test_api_error_raises_voice_intent_error(self):
        with patch.object(
            self.service, "_call_api", new_callable=AsyncMock, side_effect=VoiceIntentError("API failed")
        ):
            with pytest.raises(VoiceIntentError):
                await self.service.extract("some word")

    async def test_bad_json_from_api_returns_low_confidence(self):
        """If _call_api returns a dict that fails validation, extract() should not raise."""
        bad_response = {"season_number": "oops", "confidence": "yes-definitely"}
        with patch.object(self.service, "_call_api", new_callable=AsyncMock, return_value=bad_response):
            intent = await self.service.extract("some word")

        assert intent.confidence == "low"

    async def test_low_confidence_when_word_missing_in_response(self):
        api_response = {
            "word_or_phrase": None,
            "source_type": "unsorted",
            "analysis_mode": "general",
            "media_title": None,
            "media_type": None,
            "season_number": None,
            "episode_number": None,
            "confidence": "high",
        }
        with patch.object(self.service, "_call_api", new_callable=AsyncMock, return_value=api_response):
            intent = await self.service.extract("mumbling unclear audio")

        # GPT said high but word is None → sanitizer forces low
        assert intent.confidence == "low"
        assert intent.word_or_phrase is None
