import pytest
from pydantic import ValidationError

from app.core.config import Settings


def _base_env(**overrides: str) -> dict[str, str]:
    env = {
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "english_vocabulary",
        "POSTGRES_HOST": "db",
        "DB_PORT": "5432",
        "HOST_DB_PORT": "5432",
        "TG_BOT_TOKEN": "123456789:real-token",
        "BACKEND_HOST": "0.0.0.0",
        "BACKEND_PORT": "8000",
        "BACKEND_RELOAD": "false",
        "API_V1_PREFIX": "/api/v1",
        "FRONTEND_PORT": "5173",
        "WEBAPP_URL": "https://frontend.example.com",
        "VITE_API_URL": "/api/v1",
        "OPENAI_API_KEY": "sk-real-key",
        "OPENAI_MODEL": "gpt-4o-mini",
        "OPENAI_TIMEOUT_SECONDS": "30",
        "APP_ENV": "production",
        "LOG_LEVEL": "INFO",
        "DEFAULT_UI_LANGUAGE": "ru",
        "DEFAULT_LEARNING_LANGUAGE": "en",
        "DEFAULT_TRANSLATION_LANGUAGE": "ru",
        "CORS_ORIGINS": "http://localhost:5173,https://frontend.example.com",
        "ALLOW_DEV_AUTH_BYPASS": "true",
    }
    env.update(overrides)
    return env


def test_production_settings_disable_dev_auth_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _base_env().items():
        monkeypatch.setenv(key, value)

    settings = Settings()

    assert settings.is_production is True
    assert settings.allow_dev_auth_bypass is False
    assert settings.cors_origins == ["https://frontend.example.com"]


def test_production_settings_clear_localhost_only_cors(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _base_env(CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173").items():
        monkeypatch.setenv(key, value)

    settings = Settings()

    assert settings.cors_origins == []


def test_production_settings_reject_placeholder_bot_token(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _base_env(TG_BOT_TOKEN="your_bot_token_here").items():
        monkeypatch.setenv(key, value)

    with pytest.raises(ValidationError, match="TG_BOT_TOKEN"):
        Settings()
