from pydantic import BaseModel, Field, field_validator


class MusicSearchRequest(BaseModel):
    tg_user_id: int
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=8, ge=1, le=10)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Search query must not be empty.")
        return cleaned


class MusicTrackSearchItemResponse(BaseModel):
    provider: str
    external_id: str
    release_external_id: str | None = None
    title: str
    artist_name: str
    release_title: str | None = None
    release_year: int | None = None
    artwork_url: str | None = None
    duration_ms: int | None = None


class MusicSearchResponse(BaseModel):
    results: list[MusicTrackSearchItemResponse]
