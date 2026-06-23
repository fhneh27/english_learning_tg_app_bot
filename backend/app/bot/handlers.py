import asyncio
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import ErrorEvent, Message

from app.bot.bot_version import BOT_DISPLAY_VERSION
from app.bot.keyboards import build_app_inline_keyboard, build_app_reply_keyboard
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = Router()


async def _register_user_background(
    tg_user_id: int,
    username: str | None,
    first_name: str | None,
) -> None:
    try:
        async with AsyncSessionLocal() as session:
            user_repository = UserRepository(session)
            await user_repository.upsert_user(
                tg_user_id=tg_user_id,
                username=username,
                first_name=first_name,
            )
            await session.commit()
    except Exception:
        logger.exception("Background user registration failed for tg_user_id=%s", tg_user_id)


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    text = (
        "Send me an English word or phrase — or a <b>voice message</b>.\n\n"
        "Voice examples:\n"
        "• <i>\"I learned the word compose from Twilight, season 3\"</i>\n"
        "• <i>\"What does shallow mean in a song?\"</i>\n"
        "• <i>\"What does gring mean in slang?\"</i>\n\n"
        "I will explain it with AI, save it, and help you review it later.\n"
        "Open the Mini App to browse your vocabulary.\n\n"
        f"<i>Bot version: v{BOT_DISPLAY_VERSION}</i>"
    )
    await message.answer(
        text,
        reply_markup=build_app_inline_keyboard(),
    )
    await message.answer(
        "The Mini App button is also pinned below for quick access.",
        reply_markup=build_app_reply_keyboard(),
    )

    if message.from_user is not None:
        asyncio.create_task(
            _register_user_background(
                tg_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
        )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Commands:\n"
        "/start - show how the bot works\n"
        "/help - show this help\n"
        "/app - open the Mini App\n\n"
        "You can send an English word or phrase as text or as a <b>voice message</b>.\n\n"
        "Voice message examples:\n"
        "• <i>\"I learned the word compose from Twilight, season 3, episode 4\"</i>\n"
        "• <i>\"What does gring mean in slang?\"</i>\n"
        "• <i>\"Add the word shallow from a song\"</i>",
        reply_markup=build_app_inline_keyboard(),
    )


@router.message(Command("app"))
async def app_command(message: Message) -> None:
    await message.answer(
        "Open your vocabulary notebook in the Mini App.",
        reply_markup=build_app_inline_keyboard(),
    )


async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled bot error: %s", event.exception)
    if event.update.message is not None:
        await event.update.message.answer("Something went wrong. Please try again.")
    elif event.update.callback_query is not None:
        await event.update.callback_query.answer(
            "Something went wrong. Please try again.",
            show_alert=True,
        )
    return True
