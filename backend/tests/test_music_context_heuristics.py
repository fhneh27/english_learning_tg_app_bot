import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.music_context_heuristics import (
    enrich_intent_with_music_heuristics,
    extract_music_search_hint,
    text_mentions_music,
)
from app.services.voice_intent_service import VoiceIntent


def test_text_mentions_music_russian():
    assert text_mentions_music("это фраза из песни лил пипа veins")


def test_enrich_lil_peep_veins_message():
    intent = VoiceIntent(
        word_or_phrase="put someone on a map",
        source_type="general",
        confidence="high",
    )
    raw = 'put someone on a map, это фраза из песни лил пипа "veins"'

    enriched = enrich_intent_with_music_heuristics(raw, intent)

    assert enriched.source_type == "music"
    assert enriched.song_title == "veins"
    assert enriched.artist_name == "Lil Peep"


def test_extract_music_search_hint_without_quotes():
    raw = "put someone on a map, это фраза из песни лил пипа veins"
    hint = extract_music_search_hint(raw)
    assert hint == "Lil Peep veins"


def test_enrich_cobain_message_without_comma():
    intent = VoiceIntent(word_or_phrase=None, source_type="general", confidence="low")
    raw = "We had all of it planned out из песни лил пипа cobain"

    enriched = enrich_intent_with_music_heuristics(raw, intent)

    assert enriched.source_type == "music"
    assert enriched.song_title == "cobain"
    assert enriched.artist_name == "Lil Peep"
