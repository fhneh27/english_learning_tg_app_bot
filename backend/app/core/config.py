from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    db_port: int = Field(alias="DB_PORT")
    host_db_port: int = Field(alias="HOST_DB_PORT")

    tg_bot_token: str = Field(alias="TG_BOT_TOKEN")

    backend_host: str = Field(alias="BACKEND_HOST")
    backend_port: int = Field(alias="BACKEND_PORT")
    backend_reload: bool = Field(alias="BACKEND_RELOAD")
    api_v1_prefix: str = Field(alias="API_V1_PREFIX")

    frontend_port: int = Field(alias="FRONTEND_PORT")
    webapp_url: str = Field(alias="WEBAPP_URL")
    vite_api_url: str = Field(alias="VITE_API_URL")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(alias="OPENAI_MODEL")
    openai_timeout_seconds: int = Field(alias="OPENAI_TIMEOUT_SECONDS")
    openai_transcription_model: str = Field(default="whisper-1", alias="OPENAI_TRANSCRIPTION_MODEL")
    tmdb_api_key: str = Field(default="", alias="TMDB_API_KEY")
    tmdb_base_url: str = Field(default="https://api.themoviedb.org/3", alias="TMDB_BASE_URL")
    tmdb_image_base_url: str = Field(default="https://image.tmdb.org/t/p/w500", alias="TMDB_IMAGE_BASE_URL")
    musicbrainz_base_url: str = Field(default="https://musicbrainz.org/ws/2", alias="MUSICBRAINZ_BASE_URL")
    cover_art_archive_base_url: str = Field(default="https://coverartarchive.org", alias="COVER_ART_ARCHIVE_BASE_URL")
    musicbrainz_user_agent: str = Field(
        default="telegram-english-mini-app/1.0 (personal educational app)",
        alias="MUSICBRAINZ_USER_AGENT",
    )

    app_env: str = Field(alias="APP_ENV")
    log_level: str = Field(alias="LOG_LEVEL")
    default_ui_language: str = Field(alias="DEFAULT_UI_LANGUAGE")
    default_learning_language: str = Field(alias="DEFAULT_LEARNING_LANGUAGE")
    default_translation_language: str = Field(alias="DEFAULT_TRANSLATION_LANGUAGE")

    cors_origins_raw: str = Field(alias="CORS_ORIGINS")

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.db_port}/{self.postgres_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
