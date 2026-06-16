import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas.music import MusicTrackSearchItemResponse
from app.services.voice_music_matcher_service import VoiceMusicMatcherService


def _track(title: str, artist: str) -> MusicTrackSearchItemResponse:
    return MusicTrackSearchItemResponse(
        provider="musicbrainz",
        external_id=f"id-{title.lower()}",
        title=title,
        artist_name=artist,
    )


@pytest.mark.asyncio
async def test_music_exact_match():
    catalog = AsyncMock()
    catalog.search_tracks.return_value = [
        _track("Veins", "Lil Peep"),
        _track("Other", "Someone Else"),
    ]
    service = VoiceMusicMatcherService(catalog_service=catalog)

    result = await service.match("Lil Peep", "Veins")

    assert result.found
    assert result.track is not None
    assert result.track.title == "Veins"


@pytest.mark.asyncio
async def test_music_contains_match():
    catalog = AsyncMock()
    catalog.search_tracks.return_value = [
        _track("Veins (Remastered)", "Lil Peep"),
    ]
    service = VoiceMusicMatcherService(catalog_service=catalog)

    result = await service.match("Lil Peep", "veins")

    assert result.found


@pytest.mark.asyncio
async def test_music_no_match():
    catalog = AsyncMock()
    catalog.search_tracks.return_value = [
        _track("Unrelated", "Other Artist"),
    ]
    service = VoiceMusicMatcherService(catalog_service=catalog)

    result = await service.match("Lil Peep", "Veins")

    assert not result.found
