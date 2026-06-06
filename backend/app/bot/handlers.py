from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards import build_app_inline_keyboard, build_app_reply_keyboard
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.services.openai_service import OpenAIServiceError
from app.services.vocabulary_service import VocabularyService

router = Router()


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    if message.from_user is not None:
        async with AsyncSessionLocal() as session:
            user_repository = UserRepository(session)
            await user_repository.upsert_user(
                tg_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
            await session.commit()

    text = (
        "Send me an English word or phrase — or a <b>voice message</b>.\n\n"
        "Voice examples:\n"
        "• <i>\"I learned the word compose from Twilight, season 3\"</i>\n"
        "• <i>\"What does shallow mean in a song?\"</i>\n"
        "• <i>\"What does gring mean in slang?\"</i>\n\n"
        "I will explain it with AI, save it, and help you review it later.\n"
        "Open the Mini App to browse your vocabulary."
    )
    await message.answer(
        text,
        reply_markup=build_app_inline_keyboard(),
    )
    await message.answer(
        "The Mini App button is also pinned below for quick access.",
        reply_markup=build_app_reply_keyboard(),
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


@router.message(F.text)
async def process_text_message(message: Message) -> None:
    if message.from_user is None:
        await message.answer("I could not detect your Telegram account. Please try again.")
        return

    async with AsyncSessionLocal() as session:
        service = VocabularyService(session)
        try:
            entry = await service.create_entry(message.from_user.id, message.text)
        except ValueError:
            await message.answer("Please send a non-empty English word or phrase.")
            return
        except OpenAIServiceError:
            await message.answer("OpenAI is unavailable right now. Please try again in a moment.")
            return
        except Exception:
            await message.answer("Something went wrong while saving your entry. Please try again.")
            return

    await message.answer(_format_entry_message(entry))


def _format_entry_message(entry: object) -> str:
    original = escape(getattr(entry, "original_text", ""))
    translation = escape(getattr(entry, "translation_ru", ""))
    meaning = escape(getattr(entry, "meaning_ru", ""))
    transcription = getattr(entry, "transcription", None)
    examples: list[dict[str, str]] = getattr(entry, "examples", [])

    sections = [f"<b>{original}</b>", f"🇷🇺 {translation}"]

    if transcription:
        sections.append(f"<i>{escape(transcription)}</i>")

    sections.append(f"<b>Meaning:</b>\n{meaning}")

    if examples:
        lines = ["<b>Examples:</b>"]
        for index, example in enumerate(examples[:2], start=1):
            lines.append(
                f"{index}. {escape(example.get('en', ''))}\n"
                f"   {escape(example.get('ru', ''))}"
            )
        sections.append("\n".join(lines))

    sections.append("Saved.")
    return "\n\n".join(sections)
