from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import get_settings


def build_app_inline_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    builder = InlineKeyboardBuilder()
    builder.button(text="Open Mini App", web_app=WebAppInfo(url=settings.webapp_url))
    return builder.as_markup()


def build_app_reply_keyboard() -> ReplyKeyboardMarkup:
    settings = get_settings()
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Open Mini App",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ],
        resize_keyboard=True,
    )
