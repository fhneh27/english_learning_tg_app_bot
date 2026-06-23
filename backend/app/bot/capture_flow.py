"""Interactive vocabulary capture flow for the Telegram bot.

The bot no longer blindly saves whatever it (mis)heard. When it is not sure
about the word, it asks the user to confirm or correct it. When the user names a
source (movie / series / song) that is not yet linked to their library, the bot
searches the provider, adds it automatically when confident, and asks the user
to choose when it is not. The same flow powers both voice and text messages.

State is kept in aiogram's FSM (in-memory). Each step opens its own DB session
because the steps are driven by separate Telegram updates.
"""

import logging
from html import escape

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.entry_replies import format_capture_reply
from app.db.session import AsyncSessionLocal
from app.schemas.music import MusicTrackSearchItemResponse
from app.services.media_service import MediaService
from app.services.music_context_heuristics import extract_music_search_hint
from app.services.voice_intent_service import VoiceIntent
from app.services.voice_media_matcher_service import VoiceMediaMatcherService
from app.services.voice_music_matcher_service import VoiceMusicMatcherService
from app.services.word_capture_service import WordCaptureService

logger = logging.getLogger(__name__)

capture_router = Router()

# Callback data namespace.
CB_WORD_YES = "cap:wyes"
CB_WORD_NO = "cap:wno"
CB_MEDIA_PICK = "cap:mpick:"
CB_MEDIA_MANUAL = "cap:mmanual"
CB_MEDIA_SKIP = "cap:mskip"
CB_MUSIC_PICK = "cap:gpick:"
CB_MUSIC_MANUAL = "cap:gmanual"
CB_MUSIC_SKIP = "cap:gskip"

_MAX_CANDIDATES = 3


class CaptureStates(StatesGroup):
    confirm_word = State()
    awaiting_word = State()
    choosing_media = State()
    awaiting_media_title = State()
    choosing_music = State()
    awaiting_music_query = State()


# ── Keyboards ──────────────────────────────────────────────────────────────


def _word_confirm_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yes, that's it", callback_data=CB_WORD_YES)
    builder.button(text="✏️ No, I'll type it", callback_data=CB_WORD_NO)
    builder.adjust(1)
    return builder.as_markup()


def _media_choice_kb(candidates: list[dict]):
    builder = InlineKeyboardBuilder()
    for index, candidate in enumerate(candidates):
        year = candidate.get("year")
        kind = "Movie" if candidate.get("media_type") == "movie" else "Series"
        label = f"{candidate.get('title')}"
        if year:
            label += f" ({year})"
        label += f" · {kind}"
        builder.button(text=label[:64], callback_data=f"{CB_MEDIA_PICK}{index}")
    builder.button(text="✏️ Type the title myself", callback_data=CB_MEDIA_MANUAL)
    builder.button(text="⏭ Save without a source", callback_data=CB_MEDIA_SKIP)
    builder.adjust(1)
    return builder.as_markup()


def _music_choice_kb(candidates: list[dict]):
    builder = InlineKeyboardBuilder()
    for index, candidate in enumerate(candidates):
        label = f"{candidate.get('artist_name')} – {candidate.get('title')}"
        builder.button(text=label[:64], callback_data=f"{CB_MUSIC_PICK}{index}")
    builder.button(text="✏️ Type artist – title", callback_data=CB_MUSIC_MANUAL)
    builder.button(text="⏭ Save without a source", callback_data=CB_MUSIC_SKIP)
    builder.adjust(1)
    return builder.as_markup()


# ── Small helpers ──────────────────────────────────────────────────────────


def _title_matches(spoken: str, candidate_title: str) -> bool:
    a = (spoken or "").lower().strip()
    b = (candidate_title or "").lower().strip()
    if not a or not b:
        return False
    return a == b or a in b or b in a


def _media_filter(media_type: str | None) -> str:
    return media_type if media_type in ("movie", "series") else "all"


def _music_kwargs(track: MusicTrackSearchItemResponse) -> dict:
    return {
        "music_track_external_id": track.external_id,
        "music_release_external_id": track.release_external_id,
        "music_track_title": track.title,
        "music_artist_name": track.artist_name,
        "music_release_title": track.release_title,
        "music_release_year": track.release_year,
        "music_artwork_url": track.artwork_url,
        "music_duration_ms": track.duration_ms,
    }


async def _load_intent(state: FSMContext) -> tuple[VoiceIntent, str]:
    data = await state.get_data()
    intent = VoiceIntent(**data.get("intent", {}))
    raw_text = data.get("raw_text", "")
    return intent, raw_text


# ── Entry point ────────────────────────────────────────────────────────────


async def start_capture(message: Message, state: FSMContext, tg_user_id: int, raw_text: str) -> None:
    """Begin the capture flow for a new word/phrase from voice or text."""
    await state.clear()

    async with AsyncSessionLocal() as session:
        capture_service = WordCaptureService(session)
        intent = await capture_service.analyze(raw_text)

    if intent is None:
        # Intent API down — fall back to a plain save so the user still gets value.
        async with AsyncSessionLocal() as session:
            capture_service = WordCaptureService(session)
            result = await capture_service.legacy_save(tg_user_id, raw_text)
        await message.answer(format_capture_reply(result))
        return

    await state.update_data(raw_text=raw_text, intent=intent.model_dump())

    if intent.word_or_phrase is None:
        await state.set_state(CaptureStates.awaiting_word)
        await message.answer(
            "I couldn't catch the word clearly. Please type the English word or phrase you meant."
        )
        return

    if intent.confidence == "low":
        await state.set_state(CaptureStates.confirm_word)
        await message.answer(
            f"I heard: <b>{escape(intent.word_or_phrase)}</b>\n\nIs that the right word?",
            reply_markup=_word_confirm_kb(),
        )
        return

    await _resolve_source(message, state, tg_user_id, intent)


# ── Word confirmation ──────────────────────────────────────────────────────


@capture_router.callback_query(F.data == CB_WORD_YES, StateFilter(CaptureStates.confirm_word))
async def on_word_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    intent, _ = await _load_intent(state)
    await _clear_markup(callback)
    await callback.answer()
    await _resolve_source(callback.message, state, callback.from_user.id, intent)


@capture_router.callback_query(F.data == CB_WORD_NO, StateFilter(CaptureStates.confirm_word))
async def on_word_rejected(callback: CallbackQuery, state: FSMContext) -> None:
    await _clear_markup(callback)
    await callback.answer()
    await state.set_state(CaptureStates.awaiting_word)
    await callback.message.answer("No problem — please type the correct English word or phrase.")


@capture_router.message(StateFilter(CaptureStates.awaiting_word, CaptureStates.confirm_word), F.text)
async def on_word_typed(message: Message, state: FSMContext) -> None:
    # Covers both "please type the word" and the case where the user types the
    # correct word instead of tapping the Yes/No confirmation buttons.
    if message.from_user is None or not message.text:
        return
    intent, _ = await _load_intent(state)
    intent.word_or_phrase = message.text.strip()
    intent.confidence = "high"
    await state.update_data(intent=intent.model_dump())
    await _resolve_source(message, state, message.from_user.id, intent)


# ── Source resolution ──────────────────────────────────────────────────────


async def _resolve_source(
    message: Message,
    state: FSMContext,
    tg_user_id: int,
    intent: VoiceIntent,
) -> None:
    """Decide how to link the source, asking the user only when unsure."""
    db_source_type, db_analysis_mode = WordCaptureService._map_intent_to_db(intent)
    _, raw_text = await _load_intent(state)

    # Media source mentioned.
    if db_source_type == "media" and intent.media_title:
        async with AsyncSessionLocal() as session:
            matcher = VoiceMediaMatcherService(session)
            result = await matcher.match(
                tg_user_id=tg_user_id,
                media_title=intent.media_title,
                media_type=intent.media_type if intent.media_type in ("movie", "series") else None,
                season_number=intent.season_number,
                episode_number=intent.episode_number,
            )
        if result.found:
            label = WordCaptureService._build_media_label(
                result.matched_title, intent.season_number, intent.episode_number
            )
            await _finalize(
                message,
                state,
                tg_user_id,
                intent,
                "media",
                "general",
                media_item_id=result.media_item_id,
                media_season_id=result.media_season_id,
                media_episode_id=result.media_episode_id,
                source_label=label,
            )
            return

        await _search_and_offer_media(message, state, tg_user_id, intent, intent.media_title, from_manual=False)
        return

    # Music source mentioned.
    if WordCaptureService._should_match_music(intent, raw_text):
        hint = extract_music_search_hint(raw_text)
        matcher = VoiceMusicMatcherService()
        result = await matcher.match(
            artist_name=intent.artist_name,
            song_title=intent.song_title,
            media_title=intent.media_title,
            search_hint=hint,
        )
        if result.found and result.track is not None:
            track = result.track
            await _finalize(
                message,
                state,
                tg_user_id,
                intent,
                "music",
                "general",
                source_label=f"{track.artist_name} - {track.title}",
                music_kwargs=_music_kwargs(track),
            )
            return

        await _search_and_offer_music(message, state, tg_user_id, intent, from_manual=False)
        return

    # No special source — save as plain vocabulary.
    await _finalize(message, state, tg_user_id, intent, db_source_type, db_analysis_mode)


# ── Media search / auto-add ────────────────────────────────────────────────


async def _search_and_offer_media(
    message: Message,
    state: FSMContext,
    tg_user_id: int,
    intent: VoiceIntent,
    title: str,
    *,
    from_manual: bool,
) -> None:
    async with AsyncSessionLocal() as session:
        media_service = MediaService(session)
        try:
            results = await media_service.search(tg_user_id, title, _media_filter(intent.media_type))
        except Exception:
            logger.exception("Media search failed for title=%r", title)
            results = []

    if not results:
        if from_manual:
            await _finalize(
                message,
                state,
                tg_user_id,
                intent,
                "unsorted",
                "general",
                added_note=f"I couldn't find “{title}”, so I saved the word without a source.",
            )
            return
        await state.set_state(CaptureStates.awaiting_media_title)
        await message.answer(
            f"I couldn't find “{escape(title)}” to link. "
            "Type the exact movie/series title, or send /skip to save without a source."
        )
        return

    top = results[0]
    # Confident single match → just add it to the library, as requested.
    if _title_matches(title, top.title):
        await _add_media_and_finalize(message, state, tg_user_id, intent, top.tmdb_id, top.media_type)
        return

    # Unsure → let the user pick.
    candidates = [
        {"tmdb_id": item.tmdb_id, "media_type": item.media_type, "title": item.title, "year": item.year}
        for item in results[:_MAX_CANDIDATES]
    ]
    await state.update_data(media_candidates=candidates)
    await state.set_state(CaptureStates.choosing_media)
    await message.answer(
        f"I found a few matches for “{escape(title)}”. Which one is it?",
        reply_markup=_media_choice_kb(candidates),
    )


async def _add_media_and_finalize(
    message: Message,
    state: FSMContext,
    tg_user_id: int,
    intent: VoiceIntent,
    tmdb_id: int,
    media_type: str,
) -> None:
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    async with AsyncSessionLocal() as session:
        media_service = MediaService(session)
        try:
            card = await media_service.add_to_library(tg_user_id, tmdb_id, media_type)
        except Exception:
            logger.exception("Auto-add to library failed (tmdb_id=%s)", tmdb_id)
            await _finalize(
                message,
                state,
                tg_user_id,
                intent,
                "unsorted",
                "general",
                added_note="I couldn't add that title automatically, so I saved the word without a source.",
            )
            return

        matcher = VoiceMediaMatcherService(session)
        match = await matcher.match(
            tg_user_id=tg_user_id,
            media_title=card.title,
            media_type=media_type if media_type in ("movie", "series") else None,
            season_number=intent.season_number,
            episode_number=intent.episode_number,
        )

    media_item_id = match.media_item_id
    if media_item_id is None:
        await _finalize(
            message,
            state,
            tg_user_id,
            intent,
            "unsorted",
            "general",
            added_note=f"Added “{card.title}” to your library, but couldn't link the word — fix it in the Mini App.",
        )
        return

    label = WordCaptureService._build_media_label(card.title, intent.season_number, intent.episode_number)
    await _finalize(
        message,
        state,
        tg_user_id,
        intent,
        "media",
        "general",
        media_item_id=media_item_id,
        media_season_id=match.media_season_id,
        media_episode_id=match.media_episode_id,
        source_label=label,
        added_note=f"Added “{card.title}” to your library and linked this word to it.",
    )


@capture_router.callback_query(F.data.startswith(CB_MEDIA_PICK), StateFilter(CaptureStates.choosing_media))
async def on_media_pick(callback: CallbackQuery, state: FSMContext) -> None:
    intent, _ = await _load_intent(state)
    data = await state.get_data()
    candidates = data.get("media_candidates", [])
    try:
        index = int(callback.data.removeprefix(CB_MEDIA_PICK))
        candidate = candidates[index]
    except (ValueError, IndexError):
        await callback.answer("That option expired. Please try again.", show_alert=True)
        return
    await _clear_markup(callback)
    await callback.answer()
    await _add_media_and_finalize(
        callback.message, state, callback.from_user.id, intent, candidate["tmdb_id"], candidate["media_type"]
    )


@capture_router.callback_query(F.data == CB_MEDIA_MANUAL, StateFilter(CaptureStates.choosing_media))
async def on_media_manual(callback: CallbackQuery, state: FSMContext) -> None:
    await _clear_markup(callback)
    await callback.answer()
    await state.set_state(CaptureStates.awaiting_media_title)
    await callback.message.answer(
        "Type the exact movie or series title, or send /skip to save without a source."
    )


@capture_router.callback_query(F.data == CB_MEDIA_SKIP, StateFilter(CaptureStates.choosing_media))
async def on_media_skip(callback: CallbackQuery, state: FSMContext) -> None:
    intent, _ = await _load_intent(state)
    await _clear_markup(callback)
    await callback.answer()
    await _finalize(callback.message, state, callback.from_user.id, intent, "unsorted", "general")


@capture_router.message(
    StateFilter(CaptureStates.awaiting_media_title, CaptureStates.choosing_media), F.text
)
async def on_media_title_typed(message: Message, state: FSMContext) -> None:
    # Also handles the user typing a title instead of tapping a candidate button.
    if message.from_user is None or not message.text:
        return
    title = message.text.strip()
    if title.lower() in ("/skip", "skip"):
        intent, _ = await _load_intent(state)
        await _finalize(message, state, message.from_user.id, intent, "unsorted", "general")
        return
    intent, _ = await _load_intent(state)
    intent.media_title = title
    await state.update_data(intent=intent.model_dump())
    await _search_and_offer_media(message, state, message.from_user.id, intent, title, from_manual=True)


# ── Music search ───────────────────────────────────────────────────────────


async def _search_and_offer_music(
    message: Message,
    state: FSMContext,
    tg_user_id: int,
    intent: VoiceIntent,
    *,
    from_manual: bool,
    explicit_query: str | None = None,
) -> None:
    query = explicit_query or _build_music_query(intent)
    candidates: list[MusicTrackSearchItemResponse] = []
    if query:
        try:
            candidates = await VoiceMusicMatcherService().catalog_service.search_tracks(query, limit=8)
        except Exception:
            logger.exception("Music search failed for query=%r", query)
            candidates = []

    if not candidates:
        if from_manual:
            await _finalize(
                message,
                state,
                tg_user_id,
                intent,
                "unsorted",
                "general",
                added_note="I couldn't find that song, so I saved the word without a source.",
            )
            return
        await state.set_state(CaptureStates.awaiting_music_query)
        await message.answer(
            "I couldn't find that song to link. "
            "Type it as <b>artist – title</b>, or send /skip to save without a source."
        )
        return

    needle = (intent.song_title or intent.media_title or query or "").strip()
    top = candidates[0]
    if _title_matches(needle, top.title):
        await _finalize(
            message,
            state,
            tg_user_id,
            intent,
            "music",
            "general",
            source_label=f"{top.artist_name} - {top.title}",
            music_kwargs=_music_kwargs(top),
            added_note=f"Linked this word to “{top.artist_name} – {top.title}”.",
        )
        return

    stored = [track.model_dump() for track in candidates[:_MAX_CANDIDATES]]
    await state.update_data(music_candidates=stored)
    await state.set_state(CaptureStates.choosing_music)
    await message.answer(
        "I found a few songs. Which one is it?",
        reply_markup=_music_choice_kb(stored),
    )


def _build_music_query(intent: VoiceIntent) -> str:
    artist = (intent.artist_name or "").strip()
    song = (intent.song_title or intent.media_title or "").strip()
    return " ".join(part for part in (artist, song) if part).strip()


@capture_router.callback_query(F.data.startswith(CB_MUSIC_PICK), StateFilter(CaptureStates.choosing_music))
async def on_music_pick(callback: CallbackQuery, state: FSMContext) -> None:
    intent, _ = await _load_intent(state)
    data = await state.get_data()
    stored = data.get("music_candidates", [])
    try:
        index = int(callback.data.removeprefix(CB_MUSIC_PICK))
        track = MusicTrackSearchItemResponse(**stored[index])
    except (ValueError, IndexError, TypeError):
        await callback.answer("That option expired. Please try again.", show_alert=True)
        return
    await _clear_markup(callback)
    await callback.answer()
    await _finalize(
        callback.message,
        state,
        callback.from_user.id,
        intent,
        "music",
        "general",
        source_label=f"{track.artist_name} - {track.title}",
        music_kwargs=_music_kwargs(track),
    )


@capture_router.callback_query(F.data == CB_MUSIC_MANUAL, StateFilter(CaptureStates.choosing_music))
async def on_music_manual(callback: CallbackQuery, state: FSMContext) -> None:
    await _clear_markup(callback)
    await callback.answer()
    await state.set_state(CaptureStates.awaiting_music_query)
    await callback.message.answer(
        "Type the song as <b>artist – title</b>, or send /skip to save without a source."
    )


@capture_router.callback_query(F.data == CB_MUSIC_SKIP, StateFilter(CaptureStates.choosing_music))
async def on_music_skip(callback: CallbackQuery, state: FSMContext) -> None:
    intent, _ = await _load_intent(state)
    await _clear_markup(callback)
    await callback.answer()
    await _finalize(callback.message, state, callback.from_user.id, intent, "unsorted", "general")


@capture_router.message(
    StateFilter(CaptureStates.awaiting_music_query, CaptureStates.choosing_music), F.text
)
async def on_music_query_typed(message: Message, state: FSMContext) -> None:
    # Also handles the user typing a song instead of tapping a candidate button.
    if message.from_user is None or not message.text:
        return
    query = message.text.strip()
    intent, _ = await _load_intent(state)
    if query.lower() in ("/skip", "skip"):
        await _finalize(message, state, message.from_user.id, intent, "unsorted", "general")
        return
    await _search_and_offer_music(
        message, state, message.from_user.id, intent, from_manual=True, explicit_query=query
    )


# ── Finalize ───────────────────────────────────────────────────────────────


async def _finalize(
    message: Message,
    state: FSMContext,
    tg_user_id: int,
    intent: VoiceIntent,
    source_type: str,
    analysis_mode: str,
    *,
    media_item_id=None,
    media_season_id=None,
    media_episode_id=None,
    source_label: str | None = None,
    music_kwargs: dict | None = None,
    added_note: str | None = None,
) -> None:
    word = (intent.word_or_phrase or "").strip()
    if not word:
        await state.clear()
        await message.answer("I still don't have a word to save. Please send it again.")
        return

    if message.bot is not None:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    async with AsyncSessionLocal() as session:
        capture_service = WordCaptureService(session)
        result = await capture_service.save_entry(
            tg_user_id,
            word=word,
            source_type=source_type,
            analysis_mode=analysis_mode,
            media_item_id=media_item_id,
            media_season_id=media_season_id,
            media_episode_id=media_episode_id,
            source_label=source_label,
            music_kwargs=music_kwargs,
        )

    await state.clear()

    reply = format_capture_reply(result)
    if added_note and result.ok:
        reply = f"{added_note}\n\n{reply}"
    await message.answer(reply)


async def _clear_markup(callback: CallbackQuery) -> None:
    try:
        if callback.message is not None:
            await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        # Editing can fail if the message is too old; harmless for the flow.
        pass


@capture_router.message(StateFilter(None), F.text)
async def on_fresh_text(message: Message, state: FSMContext) -> None:
    """Start a new capture flow for a plain text word/phrase (no active state)."""
    if message.from_user is None or not message.text:
        return
    if message.bot is not None:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await start_capture(message, state, message.from_user.id, message.text)
