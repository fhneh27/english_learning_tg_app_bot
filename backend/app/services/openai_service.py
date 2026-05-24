import json
import logging

import httpx
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.vocabulary import AIVocabularyPayload

logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    """Raised when OpenAI cannot produce a valid answer."""


class OpenAIRateLimitError(OpenAIServiceError):
    """Raised when OpenAI quota or rate limit is exceeded."""


class OpenAIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def analyze_text(self, text: str) -> tuple[AIVocabularyPayload, dict]:
        payload = {
            "model": self.settings.openai_model,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_prompt(),
                },
                {
                    "role": "user",
                    "content": f"Analyze this input: {text}",
                },
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                logger.warning("OpenAI rate limit exceeded: %s", exc.response.text)
                raise OpenAIRateLimitError("OpenAI rate limit exceeded.") from exc
            logger.exception("OpenAI request failed with status %s", exc.response.status_code)
            raise OpenAIServiceError("OpenAI request failed.") from exc
        except httpx.HTTPError as exc:
            logger.exception("OpenAI request failed")
            raise OpenAIServiceError("OpenAI request failed.") from exc

        raw_response = response.json()
        text_response = self._extract_text(raw_response)

        try:
            parsed_json = json.loads(text_response)
            parsed_payload = AIVocabularyPayload.model_validate(parsed_json)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.exception("OpenAI returned invalid JSON")
            raise OpenAIServiceError("OpenAI returned invalid JSON.") from exc

        return parsed_payload, raw_response

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are helping build an English vocabulary notebook for Russian-speaking learners.\n"
            "Rules:\n"
            "- The input is English or mostly English.\n"
            "- Return only valid JSON.\n"
            "- Do not return Markdown.\n"
            "- Explain meanings in Russian.\n"
            "- Examples must be practical and natural.\n"
            "- If the input is a phrase, explain it as a phrase.\n"
            "- If there are several meanings, show the most useful ones.\n"
            "- Keep output concise but useful.\n\n"
            "Return this exact JSON shape:\n"
            "{\n"
            '  "original_text": "string",\n'
            '  "normalized_text": "string",\n'
            '  "translation_ru": "string",\n'
            '  "meaning_ru": "string",\n'
            '  "part_of_speech": "string or null",\n'
            '  "level": "string or null",\n'
            '  "transcription": "string or null",\n'
            '  "examples": [{"en": "string", "ru": "string"}],\n'
            '  "synonyms": ["string"],\n'
            '  "tags": ["string"]\n'
            "}"
        )

    @staticmethod
    def _extract_text(raw_response: dict) -> str:
        try:
            return raw_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenAIServiceError("OpenAI response format was unexpected.") from exc
