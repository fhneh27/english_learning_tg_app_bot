import json
import logging
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.models.vocabulary import VocabularyEntry
from app.schemas.user import DailyVocabularySuggestionResponse
from app.schemas.vocabulary import AIVocabularyPayload, VocabularyFollowUpResponse

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAIServiceError(Exception):
    """Raised when OpenAI cannot produce a valid answer."""


class OpenAIRateLimitError(OpenAIServiceError):
    """Raised when OpenAI quota or rate limit is exceeded."""


class OpenAIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def analyze_text(
        self,
        text: str,
        analysis_mode: str = "general",
        custom_instructions: str | None = None,
    ) -> tuple[AIVocabularyPayload, dict]:
        return await self._request_json_response(
            response_model=AIVocabularyPayload,
            system_prompt=self._build_analysis_prompt(analysis_mode, custom_instructions),
            user_content=f"Analyze this input: {text}",
            temperature=0.3,
            timeout_seconds=self.settings.openai_timeout_seconds,
        )

    async def explain_entry(
        self,
        entry: VocabularyEntry,
        prompt: str,
        custom_instructions: str | None = None,
    ) -> tuple[VocabularyFollowUpResponse, dict]:
        entry_payload = {
            "original_text": entry.original_text,
            "normalized_text": entry.normalized_text,
            "translation_ru": entry.translation_ru,
            "meaning_ru": entry.meaning_ru,
            "part_of_speech": entry.part_of_speech,
            "level": entry.level,
            "transcription": entry.transcription,
            "examples": entry.examples,
            "synonyms": entry.synonyms,
            "tags": entry.tags,
            "analysis_mode": entry.analysis_mode,
            "source_type": entry.source_type,
        }
        return await self._request_json_response(
            response_model=VocabularyFollowUpResponse,
            system_prompt=self._build_follow_up_prompt(custom_instructions),
            user_content=(
                "You are given a saved vocabulary entry and a learner follow-up question.\n"
                f"Entry JSON: {json.dumps(entry_payload, ensure_ascii=False)}\n"
                f"Learner question: {prompt}"
            ),
            temperature=0.4,
            timeout_seconds=max(self.settings.openai_timeout_seconds, 60),
        )

    async def suggest_daily_vocabulary(
        self,
        *,
        words_added_today: int,
        daily_add_goal: int,
        words_learned_today: int,
        daily_learn_goal: int,
        recent_words: list[str],
        blacklisted_suggestions: list[str],
        custom_instructions: str | None = None,
    ) -> tuple[DailyVocabularySuggestionResponse, dict]:
        remaining_add_goal = max(daily_add_goal - words_added_today, 0)
        target_count = remaining_add_goal if remaining_add_goal > 0 else 5
        request_count = min(max(target_count + 5, 8), 14)
        return await self._request_json_response(
            response_model=DailyVocabularySuggestionResponse,
            system_prompt=self._build_daily_suggestions_prompt(request_count, custom_instructions),
            user_content=(
                "Build smart English vocabulary suggestions for today.\n"
                f"Words added today: {words_added_today}\n"
                f"Daily add goal: {daily_add_goal}\n"
                f"Words learned today: {words_learned_today}\n"
                f"Daily learned goal: {daily_learn_goal}\n"
                f"Recent known words JSON: {json.dumps(recent_words, ensure_ascii=False)}\n"
                f"Permanent do-not-suggest blacklist JSON: {json.dumps(blacklisted_suggestions, ensure_ascii=False)}"
            ),
            temperature=0.85,
            timeout_seconds=max(self.settings.openai_timeout_seconds, 60),
        )

    async def _request_json_response(
        self,
        response_model: type[T],
        system_prompt: str,
        user_content: str,
        temperature: float,
        timeout_seconds: int,
    ) -> tuple[T, dict]:
        payload = {
            "model": self.settings.openai_model,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        }

        raw_response = await self._perform_request(payload, timeout_seconds)
        text_response = self._extract_text(raw_response)

        try:
            parsed_json = json.loads(text_response)
            parsed_payload = response_model.model_validate(parsed_json)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.exception("OpenAI returned invalid JSON")
            raise OpenAIServiceError("OpenAI returned invalid JSON.") from exc

        return parsed_payload, raw_response

    async def _perform_request(self, payload: dict, timeout_seconds: int) -> dict:

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
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

        return response.json()

    @staticmethod
    def _build_analysis_prompt(analysis_mode: str, custom_instructions: str | None = None) -> str:
        mode_block = {
            "general": (
                "- Focus on the standard, most useful meaning for everyday learning.\n"
                "- Keep the explanation neutral and broadly applicable.\n"
            ),
            "slang": (
                "- Treat the input as slang or very informal speech when that interpretation makes sense.\n"
                "- Explain tone, social nuance, when it sounds natural, and when it can sound rude or dated.\n"
            ),
            "conversation": (
                "- Prioritize natural spoken English and conversational usage.\n"
                "- Show how this word or phrase sounds in real dialogue and what speakers usually imply.\n"
            ),
        }[analysis_mode]

        custom_block = ""
        if custom_instructions and custom_instructions.strip():
            custom_block = f"\nUser preferences:\n{custom_instructions.strip()}\n"

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
            f"Mode guidance:\n{mode_block}\n"
            f"{custom_block}"
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
    def _build_follow_up_prompt(custom_instructions: str | None = None) -> str:
        custom_block = ""
        if custom_instructions and custom_instructions.strip():
            custom_block = f"\nUser preferences:\n{custom_instructions.strip()}\n"

        return (
            "You are helping a Russian-speaking learner understand one saved English word or phrase better.\n"
            "Rules:\n"
            "- Return only valid JSON.\n"
            "- Do not return Markdown.\n"
            "- Answer in Russian, but keep English examples natural.\n"
            "- Use the saved entry context first, then answer the learner's question directly.\n"
            "- If the question asks for more examples, give strong examples.\n"
            "- If the word is slang or conversational, explain tone and where it sounds natural.\n"
            "- Avoid long lectures; be clear, smart, and practical.\n"
            f"{custom_block}\n"
            "Return this exact JSON shape:\n"
            "{\n"
            '  "answer_ru": "string",\n'
            '  "usage_notes_ru": ["string"],\n'
            '  "mistakes_ru": ["string"],\n'
            '  "extra_examples": [{"en": "string", "ru": "string"}],\n'
            '  "follow_up_model": "string or null"\n'
            "}"
        )

    @staticmethod
    def _build_daily_suggestions_prompt(target_count: int, custom_instructions: str | None = None) -> str:
        custom_block = ""
        if custom_instructions and custom_instructions.strip():
            custom_block = f"\nUser preferences:\n{custom_instructions.strip()}\n"

        return (
            "You are helping a Russian-speaking learner decide what English vocabulary to add today.\n"
            "Rules:\n"
            "- Return only valid JSON.\n"
            "- Do not return Markdown.\n"
            "- Answer in Russian for explanations.\n"
            "- Suggest practical vocabulary for strong real-world communication.\n"
            "- Prioritize B2-C2 level, but keep the words truly useful, natural, and alive.\n"
            "- Strongly favor modern spoken English, emotionally expressive phrases, internet-aware slang, witty conversational lines, and phrases young people actually say.\n"
            "- Avoid textbook, corporate, flat, dusty, or generic classroom examples.\n"
            "- Include a balanced mix of advanced everyday words, conversational phrases, and some slang, but make them all feel current and vivid.\n"
            "- Prefer phrases with personality, social nuance, attitude, humor, or high conversational value.\n"
            "- Avoid words already present in the recent known words list.\n"
            "- Never suggest anything that appears in the permanent do-not-suggest blacklist.\n"
            "- Prefer words and phrases a person can realistically hear, read, text, or say today.\n"
            "- Keep every suggestion concise, sharp, distinct, and memorable.\n"
            "- `reason_ru` must explain why the suggestion is high-value for real life.\n"
            "- `usage_hint_ru` must sound practical and socially aware, not academic.\n"
            f"{custom_block}\n"
            f"Return exactly {target_count} suggestions.\n\n"
            "Return this exact JSON shape:\n"
            "{\n"
            '  "summary_ru": "string",\n'
            '  "target_new_words": 0,\n'
            '  "words_added_today": 0,\n'
            '  "remaining_new_words": 0,\n'
            '  "learned_today": 0,\n'
            '  "remaining_learned_words": 0,\n'
            '  "suggestions": [\n'
            "    {\n"
            '      "text": "string",\n'
            '      "kind": "word or phrase",\n'
            '      "level": "B2/C1/C2",\n'
            '      "category": "advanced/conversational/slang",\n'
            '      "reason_ru": "string",\n'
            '      "usage_hint_ru": "string"\n'
            "    }\n"
            "  ],\n"
            '  "ai_model": "string or null"\n'
            "}"
        )

    @staticmethod
    def _extract_text(raw_response: dict) -> str:
        try:
            return raw_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenAIServiceError("OpenAI response format was unexpected.") from exc
