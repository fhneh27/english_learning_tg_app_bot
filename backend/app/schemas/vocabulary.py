from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_ENTRY_STATUSES = {"new", "learning", "learned"}
VALID_SOURCE_TYPES = {"unsorted", "media", "music"}
VALID_ANALYSIS_MODES = {"general", "slang", "conversation"}


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


class VocabularyAnalyzeRequest(BaseModel):
    tg_user_id: int
    text: str = Field(min_length=1, max_length=500)
    analysis_mode: str = "general"

    @field_validator("analysis_mode")
    @classmethod
    def validate_analysis_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_ANALYSIS_MODES:
            raise ValueError("Analysis mode must be one of: general, slang, conversation.")
        return normalized


class VocabularyCreateRequest(VocabularyAnalyzeRequest):
    source_type: str = "unsorted"
    media_item_id: UUID | None = None
    media_season_id: UUID | None = None
    media_episode_id: UUID | None = None
    media_franchise_id: UUID | None = None
    music_track_external_id: str | None = Field(default=None, max_length=64)
    music_release_external_id: str | None = Field(default=None, max_length=64)
    music_track_title: str | None = Field(default=None, max_length=256)
    music_artist_name: str | None = Field(default=None, max_length=256)
    music_release_title: str | None = Field(default=None, max_length=256)
    music_release_year: int | None = None
    music_artwork_url: str | None = Field(default=None, max_length=500)
    music_duration_ms: int | None = None
    source_label: str | None = Field(default=None, max_length=256)

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_SOURCE_TYPES:
            raise ValueError("Source type must be one of: unsorted, media, music.")
        return normalized


class VocabularySaveRequest(BaseModel):
    tg_user_id: int
    analysis: AIVocabularyPayload
    source_type: str = "unsorted"
    analysis_mode: str = "general"
    media_item_id: UUID | None = None
    media_season_id: UUID | None = None
    media_episode_id: UUID | None = None
    media_franchise_id: UUID | None = None
    music_track_external_id: str | None = Field(default=None, max_length=64)
    music_release_external_id: str | None = Field(default=None, max_length=64)
    music_track_title: str | None = Field(default=None, max_length=256)
    music_artist_name: str | None = Field(default=None, max_length=256)
    music_release_title: str | None = Field(default=None, max_length=256)
    music_release_year: int | None = None
    music_artwork_url: str | None = Field(default=None, max_length=500)
    music_duration_ms: int | None = None
    source_label: str | None = Field(default=None, max_length=256)

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_SOURCE_TYPES:
            raise ValueError("Source type must be one of: unsorted, media, music.")
        return normalized

    @field_validator("analysis_mode")
    @classmethod
    def validate_analysis_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_ANALYSIS_MODES:
            raise ValueError("Analysis mode must be one of: general, slang, conversation.")
        return normalized


class VocabularyFollowUpRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=700)


class VocabularyFollowUpResponse(BaseModel):
    answer_ru: str
    usage_notes_ru: list[str] = Field(default_factory=list)
    mistakes_ru: list[str] = Field(default_factory=list)
    extra_examples: list[ExampleItem] = Field(default_factory=list)
    follow_up_model: str | None = None


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
    source_type: str
    analysis_mode: str
    media_item_id: UUID | None
    media_season_id: UUID | None
    media_episode_id: UUID | None
    media_franchise_id: UUID | None
    music_track_id: UUID | None
    source_label: str | None
    source_image_url: str | None
    repeat_count: int
    learned_at: datetime | None
    ai_model: str | None
    created_at: datetime
    updated_at: datetime


class VocabularyAnalysisResponse(BaseModel):
    analysis: AIVocabularyPayload
    ai_model: str | None
    analysis_mode: str
