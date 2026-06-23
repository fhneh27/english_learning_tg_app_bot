from functools import lru_cache

from pydantic import Field, computed_field, model_validator
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

    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_recycle_seconds: int = Field(default=1800, alias="DB_POOL_RECYCLE_SECONDS")

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

    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")

    allow_dev_auth_bypass: bool = Field(default=False, alias="ALLOW_DEV_AUTH_BYPASS")
    dev_tg_user_id: int = Field(default=123456789, alias="DEV_TG_USER_ID")
    telegram_init_data_max_age_seconds: int = Field(default=86_400, alias="TELEGRAM_INIT_DATA_MAX_AGE_SECONDS")
    ai_rate_limit_per_hour: int = Field(default=60, alias="AI_RATE_LIMIT_PER_HOUR")

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

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() in {"production", "prod"}

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        placeholder_tokens = {
            "your_bot_token_here",
            "your_openai_api_key_here",
            "your_gemini_api_key_here",
        }

        if self.is_production:
            # Never allow dev auth bypass in production, even if the env var is misconfigured.
            self.allow_dev_auth_bypass = False

            if self.tg_bot_token.strip() in placeholder_tokens:
                raise ValueError("TG_BOT_TOKEN must be set to a real bot token in production.")
            if self.openai_api_key.strip() in placeholder_tokens:
                raise ValueError("OPENAI_API_KEY must be set to a real API key in production.")

            if self.cors_origins_raw.strip():
                safe_origins = [
                    origin
                    for origin in self.cors_origins
                    if not origin.startswith("http://localhost")
                    and not origin.startswith("http://127.0.0.1")
                ]
                if safe_origins:
                    if len(safe_origins) != len(self.cors_origins):
                        self.cors_origins_raw = ",".join(safe_origins)
                else:
                    # Bot worker may inherit localhost-only CORS from the API service copy.
                    # CORS is not used by the bot process, so clear it instead of crashing.
                    self.cors_origins_raw = ""

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
