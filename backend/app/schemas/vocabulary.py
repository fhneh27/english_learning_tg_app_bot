from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_ENTRY_STATUSES = {"new", "learning", "learned"}


class ExampleItem(BaseModel):
    en: str
    ru: str


class AIVocabularyPayload(BaseModel):
    original_text: str
    normalized_text: str
    translation_ru: str
    meaning_ru: str
    part_of_speech: str | None = None
    level: str | None = None
    transcription: str | None = None
    examples: list[ExampleItem] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class VocabularyCreateRequest(BaseModel):
    tg_user_id: int
    text: str = Field(min_length=1, max_length=500)


class VocabularyStatusUpdateRequest(BaseModel):
    status: str | None = None
    increment_repetition: bool = False

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in VALID_ENTRY_STATUSES:
            raise ValueError("Status must be one of: new, learning, learned.")
        return normalized

    @model_validator(mode="after")
    def validate_payload_not_empty(self) -> "VocabularyStatusUpdateRequest":
        if self.status is None and self.increment_repetition is False:
            raise ValueError("At least one action is required: status or increment_repetition.")
        return self


class VocabularyEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tg_user_id: int
    original_text: str
    normalized_text: str
    translation_ru: str
    meaning_ru: str
    part_of_speech: str | None
    level: str | None
    transcription: str | None
    examples: list[ExampleItem]
    synonyms: list[str]
    tags: list[str]
    status: str
    repeat_count: int
    learned_at: datetime | None
    ai_model: str | None
    created_at: datetime
    updated_at: datetime
