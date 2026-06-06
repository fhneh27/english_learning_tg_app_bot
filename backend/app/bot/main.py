import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.bot.handlers import router
from app.bot.voice_handler import voice_router
from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    # Voice handler must be registered before the generic text handler.
    dispatcher.include_router(voice_router)
    dispatcher.include_router(router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="How the vocabulary bot works"),
            BotCommand(command="help", description="Show help"),
            BotCommand(command="app", description="Open the Mini App"),
        ]
    )

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
