import logging
from dataclasses import dataclass

from app.schemas.music import MusicTrackSearchItemResponse
from app.services.music_catalog_service import MusicCatalogService, MusicCatalogServiceError

logger = logging.getLogger(__name__)


@dataclass
class MusicMatchResult:
    track: MusicTrackSearchItemResponse | None = None

    @property
    def found(self) -> bool:
        return self.track is not None


class VoiceMusicMatcherService:
    """Match extracted song metadata against MusicBrainz search results."""

    def __init__(self, catalog_service: MusicCatalogService | None = None) -> None:
        self.catalog_service = catalog_service or MusicCatalogService()

    async def match(
        self,
        artist_name: str | None,
        song_title: str | None,
        media_title: str | None = None,
    ) -> MusicMatchResult:
        query = self._build_search_query(artist_name, song_title, media_title)
        if not query:
            return MusicMatchResult()

        try:
            candidates = await self.catalog_service.search_tracks(query, limit=5)
        except MusicCatalogServiceError:
            logger.exception("MusicBrainz search failed for query=%r", query)
            return MusicMatchResult()

        if not candidates:
            logger.info("No music candidates for query=%r", query)
            return MusicMatchResult()

        needle_song = self._normalize(song_title or media_title or "")
        needle_artist = self._normalize(artist_name or "")

        # Pass 1: exact normalized title + artist match.
        for track in candidates:
            if self._is_exact_match(track, needle_song, needle_artist):
                logger.info("Music exact match: %s - %s", track.artist_name, track.title)
                return MusicMatchResult(track=track)

        # Pass 2: contains match on title and artist.
        for track in candidates:
            if self._is_contains_match(track, needle_song, needle_artist):
                logger.info("Music contains match: %s - %s", track.artist_name, track.title)
                return MusicMatchResult(track=track)

        logger.info("No music match for query=%r", query)
        return MusicMatchResult()

    @staticmethod
    def _build_search_query(
        artist_name: str | None,
        song_title: str | None,
        media_title: str | None,
    ) -> str:
        parts = [part.strip() for part in (artist_name, song_title or media_title) if part and part.strip()]
        return " ".join(parts)

    @staticmethod
    def _normalize(value: str) -> str:
        return value.lower().strip()

    @staticmethod
    def _is_exact_match(
        track: MusicTrackSearchItemResponse,
        needle_song: str,
        needle_artist: str,
    ) -> bool:
        if not needle_song:
            return False
        title = track.title.lower().strip()
        artist = track.artist_name.lower().strip()
        if title != needle_song:
            return False
        if not needle_artist:
            return True
        return needle_artist == artist or needle_artist in artist or artist in needle_artist

    @staticmethod
    def _is_contains_match(
        track: MusicTrackSearchItemResponse,
        needle_song: str,
        needle_artist: str,
    ) -> bool:
        if not needle_song:
            return False
        title = track.title.lower().strip()
        artist = track.artist_name.lower().strip()
        title_match = needle_song in title or title in needle_song
        if not title_match:
            return False
        if not needle_artist:
            return True
        return needle_artist in artist or artist in needle_artist
