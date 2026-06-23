import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.bot.capture_flow import capture_router
from app.bot.handlers import global_error_handler, router
from app.bot.voice_handler import voice_router
from app.core.config import get_settings
from app.core.logging import configure_logging


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.errors.register(global_error_handler)
    # Order matters: voice first, then commands, then the interactive capture
    # flow (which owns all generic text + confirmation callbacks/states).
    dispatcher.include_router(voice_router)
    dispatcher.include_router(router)
    dispatcher.include_router(capture_router)

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
