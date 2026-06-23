from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.rate_limit import RateLimitExceeded, check_rate_limit
from app.core.telegram_auth import TelegramAuthError, extract_tg_user_id, validate_telegram_init_data


def get_authenticated_tg_user_id(
    x_telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
    x_dev_tg_user_id: str | None = Header(default=None, alias="X-Dev-Tg-User-Id"),
    settings: Settings = Depends(get_settings),
) -> int:
    if x_telegram_init_data:
        try:
            parsed = validate_telegram_init_data(
                x_telegram_init_data,
                settings.tg_bot_token,
                max_age_seconds=settings.telegram_init_data_max_age_seconds,
            )
            return extract_tg_user_id(parsed)
        except TelegramAuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram authentication.",
            ) from exc

    if settings.allow_dev_auth_bypass and not settings.is_production:
        if x_dev_tg_user_id:
            try:
                dev_user_id = int(x_dev_tg_user_id)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid development user id.",
                ) from exc
            if dev_user_id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid development user id.",
                )
            return dev_user_id
        return settings.dev_tg_user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )


def enforce_ai_rate_limit(
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    settings: Settings = Depends(get_settings),
) -> int:
    try:
        check_rate_limit(
            key=f"ai:{tg_user_id}",
            max_requests=settings.ai_rate_limit_per_hour,
            window_seconds=3600,
        )
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many AI requests. Please try again later.",
        ) from exc
    return tg_user_id


def assert_matching_tg_user_id(requested_tg_user_id: int, authenticated_tg_user_id: int) -> None:
    if requested_tg_user_id != authenticated_tg_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Telegram user id mismatch.",
        )
