import asyncio
import time

import httpx

from app.core.config import get_settings
from app.schemas.music import MusicTrackSearchItemResponse


class MusicCatalogServiceError(Exception):
    """Raised when external music catalog could not provide data."""


class MusicCatalogService:
    _rate_lock = asyncio.Lock()
    _last_request_at = 0.0

    def __init__(self) -> None:
        self.settings = get_settings()

    async def search_tracks(self, query: str, limit: int = 8) -> list[MusicTrackSearchItemResponse]:
        cleaned_query = " ".join(query.strip().split())
        if not cleaned_query:
            return []

        await self._respect_rate_limit()

        params = {
            "query": cleaned_query,
            "fmt": "json",
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(
                timeout=30,
                headers={"User-Agent": self.settings.musicbrainz_user_agent},
            ) as client:
                response = await client.get(f"{self.settings.musicbrainz_base_url}/recording/", params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MusicCatalogServiceError("Music catalog is unavailable right now.") from exc

        payload = response.json()
        recordings = payload.get("recordings", [])

        results: list[MusicTrackSearchItemResponse] = []
        seen: set[tuple[str, str]] = set()

        for recording in recordings:
            title = (recording.get("title") or "").strip()
            artist_name = self._build_artist_name(recording.get("artist-credit") or [])
            if not title or not artist_name:
                continue

            dedupe_key = (title.lower(), artist_name.lower())
            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            best_release = self._pick_best_release(recording.get("releases") or [])
            release_id = best_release.get("id") if best_release else None
            release_title = (best_release.get("title") or "").strip() or None if best_release else None
            release_year = self._extract_year(best_release.get("date")) if best_release else None
            if release_year is None:
                release_year = self._extract_year(recording.get("first-release-date"))

            results.append(
                MusicTrackSearchItemResponse(
                    provider="musicbrainz",
                    external_id=recording.get("id") or "",
                    release_external_id=release_id,
                    title=title,
                    artist_name=artist_name,
                    release_title=release_title,
                    release_year=release_year,
                    artwork_url=self._build_artwork_url(release_id),
                    duration_ms=recording.get("length"),
                )
            )

            if len(results) >= limit:
                break

        return results

    async def _respect_rate_limit(self) -> None:
        async with self._rate_lock:
            now = time.monotonic()
            wait_seconds = 1.05 - (now - self._last_request_at)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            self.__class__._last_request_at = time.monotonic()

    @staticmethod
    def _build_artist_name(artist_credit: list[dict]) -> str:
        names: list[str] = []
        for item in artist_credit:
            name = (item.get("name") or "").strip()
            if name:
                names.append(name)
        return ", ".join(names)

    @staticmethod
    def _extract_year(date_value: str | None) -> int | None:
        if not date_value or len(date_value) < 4:
            return None
        year = date_value[:4]
        return int(year) if year.isdigit() else None

    @staticmethod
    def _pick_best_release(releases: list[dict]) -> dict | None:
        if not releases:
            return None

        def release_sort_key(item: dict) -> tuple[int, int, int, str]:
            status = (item.get("status") or "").lower()
            primary_type = ((item.get("release-group") or {}).get("primary-type") or "").lower()
            year = MusicCatalogService._extract_year(item.get("date")) or 9999

            status_rank = 0 if status == "official" else 1
            primary_rank = 0 if primary_type in {"album", "single", "ep"} else 1
            return (status_rank, primary_rank, year, (item.get("title") or "").lower())

        return sorted(releases, key=release_sort_key)[0]

    def _build_artwork_url(self, release_id: str | None) -> str | None:
        if not release_id:
            return None
        return f"{self.settings.cover_art_archive_base_url}/release/{release_id}/front-250"
