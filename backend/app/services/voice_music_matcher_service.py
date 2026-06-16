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
        *,
        search_hint: str | None = None,
    ) -> MusicMatchResult:
        queries = self._build_search_queries(artist_name, song_title, media_title, search_hint)
        if not queries:
            return MusicMatchResult()

        needle_song = self._normalize(song_title or media_title or "")
        needle_artist = self._normalize(artist_name or "")

        for query in queries:
            try:
                candidates = await self.catalog_service.search_tracks(query, limit=8)
            except MusicCatalogServiceError:
                logger.exception("MusicBrainz search failed for query=%r", query)
                continue

            if not candidates:
                logger.info("No music candidates for query=%r", query)
                continue

            matched = self._pick_best_match(candidates, needle_song, needle_artist, query)
            if matched is not None:
                logger.info("Music match via query=%r: %s - %s", query, matched.artist_name, matched.title)
                return MusicMatchResult(track=matched)

        logger.info("No music match for queries=%r", queries)
        return MusicMatchResult()

    def _pick_best_match(
        self,
        candidates: list[MusicTrackSearchItemResponse],
        needle_song: str,
        needle_artist: str,
        query: str,
    ) -> MusicTrackSearchItemResponse | None:
        for track in candidates:
            if self._is_exact_match(track, needle_song, needle_artist):
                return track

        for track in candidates:
            if self._is_contains_match(track, needle_song, needle_artist):
                return track

        if needle_song:
            for track in candidates:
                title = track.title.lower().strip()
                if needle_song in title or title in needle_song:
                    if not needle_artist:
                        return track
                    artist = track.artist_name.lower().strip()
                    if needle_artist in artist or artist in needle_artist:
                        return track

        query_tokens = [token for token in self._normalize(query).split() if len(token) >= 3]
        if query_tokens:
            for track in candidates:
                haystack = f"{track.title} {track.artist_name}".lower()
                if all(token in haystack for token in query_tokens):
                    return track

        return None

    @staticmethod
    def _build_search_queries(
        artist_name: str | None,
        song_title: str | None,
        media_title: str | None,
        search_hint: str | None,
    ) -> list[str]:
        queries: list[str] = []
        artist = (artist_name or "").strip()
        song = (song_title or media_title or "").strip()
        hint = (search_hint or "").strip()

        if artist and song:
            queries.append(f'artist:"{artist}" AND recording:"{song}"')
            queries.append(f"{artist} {song}")
        elif song:
            queries.append(f'recording:"{song}"')
            queries.append(song)
        elif artist:
            queries.append(f'artist:"{artist}"')
            queries.append(artist)

        if hint and hint not in queries:
            queries.append(hint)

        deduped: list[str] = []
        for query in queries:
            if query and query not in deduped:
                deduped.append(query)
        return deduped

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
