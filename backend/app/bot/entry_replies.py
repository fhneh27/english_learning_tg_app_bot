from html import escape

from app.services.word_capture_service import WordCaptureResult


def format_capture_reply(result: WordCaptureResult) -> str:
    if not result.ok or result.entry is None:
        return result.error_message or "Something went wrong. Please try again."

    entry = result.entry
    original = escape(entry.original_text)
    translation = escape(entry.translation_ru)
    meaning = escape(entry.meaning_ru)
    transcription = entry.transcription
    examples = entry.examples or []

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

    if result.source_label:
        sections.append(f"<i>Source: {escape(result.source_label)}</i>")

    if result.media_not_found:
        sections.append(
            "Word saved, but I couldn't find the media source in your library. "
            "You can link it manually in the Mini App."
        )
    elif result.music_not_found:
        sections.append(
            "Word saved, but I couldn't find the exact song. "
            "You can link it manually in the Mini App."
        )
    else:
        sections.append("Saved.")

    return "\n\n".join(sections)
