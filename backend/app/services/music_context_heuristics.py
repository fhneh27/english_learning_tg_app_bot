import re

from app.services.voice_intent_service import VoiceIntent

_MUSIC_HINTS = (
    "песн",
    " song",
    "song ",
    "трек",
    " track",
    "track ",
    "music",
    "музык",
)

_ARTIST_ALIASES = {
    "лил пип": "Lil Peep",
    "лил пипа": "Lil Peep",
    "lil peep": "Lil Peep",
}


def text_mentions_music(raw_text: str) -> bool:
    lowered = raw_text.lower()
    return any(hint in lowered for hint in _MUSIC_HINTS)


def enrich_intent_with_music_heuristics(raw_text: str, intent: VoiceIntent) -> VoiceIntent:
    """Fill missing music fields from mixed RU/EN bot messages."""
    if not text_mentions_music(raw_text):
        return intent

    intent.source_type = "music"
    intent.media_type = "song"

    quoted = re.search(r'["\'«]([^"\']+)["\'»]', raw_text)
    if quoted and not intent.song_title:
        intent.song_title = quoted.group(1).strip()

    tail_match = re.search(
        r"(?:из песни|from (?:the )?song|from song|from)\s+(.+)$",
        raw_text,
        flags=re.IGNORECASE,
    )
    if tail_match:
        tail = tail_match.group(1).strip().strip('"\'«».,')
        artist, song = _split_artist_and_song(tail)
        if song and not intent.song_title:
            intent.song_title = song
        if artist and not intent.artist_name:
            intent.artist_name = _normalize_artist_name(artist)

    if intent.artist_name:
        intent.artist_name = _normalize_artist_name(intent.artist_name)

    if intent.word_or_phrase and intent.confidence == "low":
        intent.confidence = "high"

    return intent


def extract_music_search_hint(raw_text: str) -> str | None:
    """Return a free-form MusicBrainz query extracted from user text."""
    quoted = re.search(r'["\'«]([^"\']+)["\'»]', raw_text)
    if quoted:
        before = raw_text[: quoted.start()]
        tail_match = re.search(
            r"(?:из песни|from (?:the )?song|from song|from)\s+(.+)$",
            before,
            flags=re.IGNORECASE,
        )
        if tail_match:
            artist = _normalize_artist_name(tail_match.group(1).strip().strip('"\'«».,'))
            return f"{artist} {quoted.group(1).strip()}".strip()

    tail_match = re.search(
        r"(?:из песни|from (?:the )?song|from song|from)\s+(.+)$",
        raw_text,
        flags=re.IGNORECASE,
    )
    if not tail_match:
        return None

    tail = tail_match.group(1).strip().strip('"\'«».,')
    artist, song = _split_artist_and_song(tail)
    if artist and song:
        return f"{_normalize_artist_name(artist)} {song}".strip()
    return _normalize_artist_name(tail) or tail or None


def _split_artist_and_song(tail: str) -> tuple[str | None, str | None]:
    cleaned = tail.strip().strip('"\'«».,')
    if not cleaned:
        return None, None

    tokens = cleaned.split()
    if len(tokens) >= 2 and tokens[-1].isascii() and tokens[-1].isalpha():
        artist = " ".join(tokens[:-1]).strip()
        song = tokens[-1].strip()
        return artist or None, song or None

    return cleaned, None


def _normalize_artist_name(name: str) -> str:
    lowered = name.lower().strip()
    for alias, canonical in _ARTIST_ALIASES.items():
        if alias in lowered:
            return canonical
    return name.strip()
