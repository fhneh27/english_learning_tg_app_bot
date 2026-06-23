import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl


class TelegramAuthError(Exception):
    """Raised when Telegram WebApp init data fails validation."""


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 86_400,
) -> dict[str, str]:
    """Validate Telegram Mini App initData using the official HMAC algorithm."""
    if not init_data.strip():
        raise TelegramAuthError("Init data is empty.")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Init data is missing hash.")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("Init data hash mismatch.")

    auth_date_raw = parsed.get("auth_date")
    if not auth_date_raw:
        raise TelegramAuthError("Init data is missing auth_date.")

    try:
        auth_date = int(auth_date_raw)
    except ValueError as exc:
        raise TelegramAuthError("Init data auth_date is invalid.") from exc

    if auth_date <= 0:
        raise TelegramAuthError("Init data auth_date is invalid.")

    age_seconds = time.time() - auth_date
    if age_seconds > max_age_seconds:
        raise TelegramAuthError("Init data expired.")
    if age_seconds < -300:
        raise TelegramAuthError("Init data auth_date is in the future.")

    return parsed


def extract_tg_user_id(parsed_init_data: dict[str, str]) -> int:
    user_json = parsed_init_data.get("user")
    if not user_json:
        raise TelegramAuthError("Init data is missing user.")

    try:
        user = json.loads(user_json)
        tg_user_id = int(user["id"])
    except (TypeError, ValueError, KeyError) as exc:
        raise TelegramAuthError("Init data user payload is invalid.") from exc

    if tg_user_id <= 0:
        raise TelegramAuthError("Init data user id is invalid.")

    return tg_user_id
