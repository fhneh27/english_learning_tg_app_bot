import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TMDBServiceError(Exception):
    """Raised when TMDB request fails."""


class TMDBService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.tmdb_base_url.rstrip("/")

    async def search(self, query: str, filter_type: str) -> list[dict]:
        endpoint = "/search/multi" if filter_type == "all" else f"/search/{'movie' if filter_type == 'movie' else 'tv'}"
        response = await self._request(endpoint, {"query": query})
        results = response.get("results", [])

        normalized: list[dict] = []
        for raw_item in results:
            media_type = raw_item.get("media_type")
            if filter_type == "movie":
                media_type = "movie"
            if filter_type == "series":
                media_type = "tv"
            if media_type not in {"movie", "tv"}:
                continue

            title = raw_item.get("title") or raw_item.get("name")
            if not title:
                continue
            release_date = raw_item.get("release_date") or raw_item.get("first_air_date")
            year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
            normalized.append(
                {
                    "tmdb_id": raw_item["id"],
                    "media_type": "movie" if media_type == "movie" else "series",
                    "title": title,
                    "year": year,
                    "poster_path": raw_item.get("poster_path"),
                    "overview": raw_item.get("overview"),
                }
            )
        return normalized

    async def get_movie_details(self, tmdb_id: int) -> dict:
        return await self._request(f"/movie/{tmdb_id}")

    async def get_collection_details(self, tmdb_collection_id: int) -> dict:
        return await self._request(f"/collection/{tmdb_collection_id}")

    async def get_tv_details(self, tmdb_id: int) -> dict:
        return await self._request(f"/tv/{tmdb_id}")

    async def get_tv_season_details(self, tmdb_id: int, season_number: int) -> dict:
        return await self._request(f"/tv/{tmdb_id}/season/{season_number}")

    async def _request(self, path: str, params: dict | None = None) -> dict:
        if not self.settings.tmdb_api_key:
            raise TMDBServiceError("TMDB API key is not configured.")
        query_params = {"api_key": self.settings.tmdb_api_key}
        if params:
            query_params.update(params)

        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(url, params=query_params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.exception("TMDB request failed: %s", path)
            raise TMDBServiceError("TMDB request failed.") from exc
