import hashlib
import hmac
import json
import time

import pytest

from app.core.telegram_auth import TelegramAuthError, extract_tg_user_id, validate_telegram_init_data


def _build_init_data(bot_token: str, user_id: int, auth_date: int | None = None) -> str:
    auth_ts = auth_date if auth_date is not None else int(time.time())
    user_payload = json.dumps({"id": user_id, "first_name": "Test"}, separators=(",", ":"))
    pairs = {
        "auth_date": str(auth_ts),
        "query_id": "AAE",
        "user": user_payload,
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    init_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return "&".join(f"{key}={value}" for key, value in [*sorted(pairs.items()), ("hash", init_hash)])


def test_validate_init_data_accepts_valid_signature() -> None:
    bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    init_data = _build_init_data(bot_token, 424242)

    parsed = validate_telegram_init_data(init_data, bot_token, max_age_seconds=3600)

    assert extract_tg_user_id(parsed) == 424242


def test_validate_init_data_rejects_tampered_user() -> None:
    bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    init_data = _build_init_data(bot_token, 424242).replace("424242", "999999")

    with pytest.raises(TelegramAuthError):
        validate_telegram_init_data(init_data, bot_token, max_age_seconds=3600)


def test_validate_init_data_rejects_expired_payload() -> None:
    bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    expired_auth_date = int(time.time()) - 10_000
    init_data = _build_init_data(bot_token, 424242, auth_date=expired_auth_date)

    with pytest.raises(TelegramAuthError, match="expired"):
        validate_telegram_init_data(init_data, bot_token, max_age_seconds=3600)
