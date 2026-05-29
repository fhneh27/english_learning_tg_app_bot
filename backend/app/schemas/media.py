from uuid import UUID

from pydantic import BaseModel, Field, field_validator

VALID_MEDIA_TYPES = {"movie", "series", "franchise"}
VALID_MEDIA_SEARCH_FILTERS = {"all", "movie", "series"}
VALID_MEDIA_VOCAB_SCOPES = {"movie", "series", "franchise"}


class MediaSearchRequest(BaseModel):
    tg_user_id: int
    query: str = Field(min_length=1, max_length=200)
    filter_type: str = "all"

    @field_validator("filter_type")
    @classmethod
    def validate_filter_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_MEDIA_SEARCH_FILTERS:
            raise ValueError("Filter must be one of: all, movie, series.")
        return normalized


class MediaSearchItemResponse(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    year: int | None
    poster_path: str | None
    overview: str | None
    is_in_library: bool = False


class MediaSearchResponse(BaseModel):
    results: list[MediaSearchItemResponse]


class MediaAddRequest(BaseModel):
    tg_user_id: int
    tmdb_id: int
    media_type: str

    @field_validator("media_type")
    @classmethod
    def validate_media_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"movie", "series"}:
            raise ValueError("Media type must be one of: movie, series.")
        return normalized


class MediaCardResponse(BaseModel):
    id: UUID
    tmdb_id: int | None
    media_type: str
    title: str
    year: int | None
    poster_path: str | None
    overview: str | None
    runtime_minutes: int
    watched_minutes: int
    watched_percent: int
    is_watched: bool


class MediaLibraryResponse(BaseModel):
    movies: list[MediaCardResponse]
    series: list[MediaCardResponse]
    franchises: list[MediaCardResponse]


class VocabularyWordShortResponse(BaseModel):
    id: UUID
    original_text: str
    translation_ru: str
    meaning_ru: str
    status: str
    source_label: str | None
    media_kind: str | None


class MediaSeasonCardResponse(BaseModel):
    id: UUID
    season_number: int
    title: str
    overview: str | None
    episode_count: int
    watched_episodes: int
    watched_percent: int


class MediaEpisodeCardResponse(BaseModel):
    id: UUID
    season_number: int
    episode_number: int
    title: str
    overview: str | None
    runtime_minutes: int
    watched_minutes: int
    watched_percent: int
    is_watched: bool


class MovieDetailResponse(BaseModel):
    item: MediaCardResponse
    watched_label: str
    words: list[VocabularyWordShortResponse]


class SeriesDetailResponse(BaseModel):
    item: MediaCardResponse
    seasons: list[MediaSeasonCardResponse]
    total_episodes: int
    watched_episodes: int
    words: list[VocabularyWordShortResponse]


class SeasonDetailResponse(BaseModel):
    series_item_id: UUID
    season: MediaSeasonCardResponse
    episodes: list[MediaEpisodeCardResponse]
    words: list[VocabularyWordShortResponse]


class EpisodeDetailResponse(BaseModel):
    series_item_id: UUID
    season_id: UUID
    episode: MediaEpisodeCardResponse
    watched_label: str
    words: list[VocabularyWordShortResponse]


class FranchiseDetailResponse(BaseModel):
    item: MediaCardResponse
    movies: list[MediaCardResponse]
    total_runtime_minutes: int
    watched_minutes: int
    watched_percent: int
    words: list[VocabularyWordShortResponse]


class MediaProgressUpdateRequest(BaseModel):
    tg_user_id: int
    watched_minutes: int | None = Field(default=None, ge=0)
    mark_watched: bool = False


class MediaVocabularyResponse(BaseModel):
    words: list[VocabularyWordShortResponse]
