from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import MediaEpisode, MediaItem, MediaSeason
from app.repositories.media_repository import MediaRepository
from app.repositories.user_repository import UserRepository
from app.schemas.media import (
    EpisodeDetailResponse,
    FranchiseDetailResponse,
    MediaCardResponse,
    MediaEpisodeCardResponse,
    MediaLibraryResponse,
    MediaSeasonCardResponse,
    MediaSearchItemResponse,
    MovieDetailResponse,
    SeasonDetailResponse,
    SeriesDetailResponse,
    VALID_MEDIA_VOCAB_SCOPES,
    VocabularyWordShortResponse,
)
from app.services.tmdb_service import TMDBService


class MediaNotFoundError(Exception):
    """Raised when requested media entity does not exist for this user."""


class MediaService:
    def __init__(
        self,
        session: AsyncSession,
        media_repository: MediaRepository | None = None,
        user_repository: UserRepository | None = None,
        tmdb_service: TMDBService | None = None,
    ) -> None:
        self.session = session
        self.media_repository = media_repository or MediaRepository(session)
        self.user_repository = user_repository or UserRepository(session)
        self.tmdb_service = tmdb_service or TMDBService()

    async def search(self, tg_user_id: int, query: str, filter_type: str) -> list[MediaSearchItemResponse]:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        search_items = await self.tmdb_service.search(query, filter_type)
        library = await self.media_repository.get_library_items(tg_user_id)
        existing_pairs = {(item.media_type, item.tmdb_id) for item in library if item.tmdb_id is not None}

        results: list[MediaSearchItemResponse] = []
        for item in search_items:
            results.append(
                MediaSearchItemResponse(
                    tmdb_id=item["tmdb_id"],
                    media_type=item["media_type"],
                    title=item["title"],
                    year=item["year"],
                    poster_path=item["poster_path"],
                    overview=item["overview"],
                    is_in_library=(item["media_type"], item["tmdb_id"]) in existing_pairs,
                )
            )
        return results

    async def add_to_library(self, tg_user_id: int, tmdb_id: int, media_type: str) -> MediaCardResponse:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        if media_type == "movie":
            item = await self._add_movie(tg_user_id, tmdb_id)
        else:
            item = await self._add_series(tg_user_id, tmdb_id)
        await self.session.commit()
        await self.session.refresh(item)
        return self._to_media_card(item)

    async def get_library(self, tg_user_id: int) -> MediaLibraryResponse:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        items = await self.media_repository.get_library_items(tg_user_id)

        movies = [self._to_media_card(item) for item in items if item.media_type == "movie"]
        series = [self._to_media_card(item) for item in items if item.media_type == "series"]
        franchises = [self._to_media_card(item) for item in items if item.media_type == "franchise"]
        return MediaLibraryResponse(movies=movies, series=series, franchises=franchises)

    async def get_movie_detail(self, item_id: UUID, tg_user_id: int) -> MovieDetailResponse:
        item = await self._require_item(item_id, tg_user_id, "movie")
        words = await self.media_repository.list_words_for_media_item(item.id, tg_user_id)
        return MovieDetailResponse(
            item=self._to_media_card(item),
            watched_label=f"{item.watched_minutes} / {max(item.runtime_minutes, 0)} min",
            words=self._to_word_short_list(words, "movie"),
        )

    async def get_series_detail(self, item_id: UUID, tg_user_id: int) -> SeriesDetailResponse:
        item = await self._require_item(item_id, tg_user_id, "series")
        seasons = await self.media_repository.list_seasons(item.id)
        episodes_by_season = {
            season.id: await self.media_repository.list_episodes(season.id) for season in seasons
        }
        season_cards = [self._to_season_card(season, episodes_by_season.get(season.id, [])) for season in seasons]
        total_episodes = sum(len(episodes) for episodes in episodes_by_season.values())
        watched_episodes = sum(
            1 for episodes in episodes_by_season.values() for episode in episodes if episode.is_watched
        )

        series_words = await self.media_repository.list_words_for_media_item(item.id, tg_user_id)
        for season in seasons:
            series_words.extend(await self.media_repository.list_words_for_season(season.id, tg_user_id))
            for episode in episodes_by_season.get(season.id, []):
                series_words.extend(await self.media_repository.list_words_for_episode(episode.id, tg_user_id))

        return SeriesDetailResponse(
            item=self._to_media_card(item),
            seasons=season_cards,
            total_episodes=total_episodes,
            watched_episodes=watched_episodes,
            words=self._to_word_short_list(series_words, "series"),
        )

    async def get_season_detail(self, season_id: UUID, tg_user_id: int) -> SeasonDetailResponse:
        season = await self.media_repository.get_season(season_id)
        if season is None:
            raise MediaNotFoundError("Season not found.")

        series_item = await self.media_repository.get_item_by_id(season.series_item_id, tg_user_id)
        if series_item is None or series_item.media_type != "series":
            raise MediaNotFoundError("Season not found.")

        episodes = await self.media_repository.list_episodes(season.id)
        season_words = await self.media_repository.list_words_for_season(season.id, tg_user_id)
        for episode in episodes:
            season_words.extend(await self.media_repository.list_words_for_episode(episode.id, tg_user_id))

        return SeasonDetailResponse(
            series_item_id=series_item.id,
            season=self._to_season_card(season, episodes),
            episodes=[self._to_episode_card(episode) for episode in episodes],
            words=self._to_word_short_list(season_words, "series"),
        )

    async def get_episode_detail(self, episode_id: UUID, tg_user_id: int) -> EpisodeDetailResponse:
        episode = await self.media_repository.get_episode(episode_id)
        if episode is None:
            raise MediaNotFoundError("Episode not found.")

        series_item = await self.media_repository.get_item_by_id(episode.series_item_id, tg_user_id)
        if series_item is None or series_item.media_type != "series":
            raise MediaNotFoundError("Episode not found.")

        words = await self.media_repository.list_words_for_episode(episode.id, tg_user_id)
        return EpisodeDetailResponse(
            series_item_id=episode.series_item_id,
            season_id=episode.season_id,
            episode=self._to_episode_card(episode),
            watched_label=f"{episode.watched_minutes} / {max(episode.runtime_minutes, 0)} min",
            words=self._to_word_short_list(words, "series"),
        )

    async def get_franchise_detail(self, item_id: UUID, tg_user_id: int) -> FranchiseDetailResponse:
        item = await self._require_item(item_id, tg_user_id, "franchise")
        movies = await self.media_repository.list_franchise_movies(item.id)
        words = await self.media_repository.list_words_for_franchise(item.id, tg_user_id)
        for movie in movies:
            words.extend(await self.media_repository.list_words_for_media_item(movie.id, tg_user_id))

        total_runtime = sum(max(movie.runtime_minutes, 0) for movie in movies)
        watched_minutes = sum(max(movie.watched_minutes, 0) for movie in movies)
        watched_percent = self._progress_percent(watched_minutes, total_runtime)

        return FranchiseDetailResponse(
            item=self._to_media_card(item),
            movies=[self._to_media_card(movie) for movie in movies],
            total_runtime_minutes=total_runtime,
            watched_minutes=watched_minutes,
            watched_percent=watched_percent,
            words=self._to_word_short_list(words, "franchise"),
        )

    async def update_movie_progress(
        self,
        item_id: UUID,
        tg_user_id: int,
        watched_minutes: int | None,
        mark_watched: bool,
    ) -> MediaCardResponse:
        item = await self._require_item(item_id, tg_user_id, "movie")
        runtime = max(item.runtime_minutes, 0)

        if mark_watched:
            item.watched_minutes = runtime
        elif watched_minutes is not None:
            item.watched_minutes = min(max(watched_minutes, 0), runtime if runtime > 0 else watched_minutes)

        item.is_watched = runtime > 0 and item.watched_minutes >= runtime
        await self.session.commit()
        await self.session.refresh(item)
        return self._to_media_card(item)

    async def update_episode_progress(
        self,
        episode_id: UUID,
        tg_user_id: int,
        watched_minutes: int | None,
        mark_watched: bool,
    ) -> MediaEpisodeCardResponse:
        episode = await self.media_repository.get_episode(episode_id)
        if episode is None:
            raise MediaNotFoundError("Episode not found.")
        series_item = await self.media_repository.get_item_by_id(episode.series_item_id, tg_user_id)
        if series_item is None or series_item.media_type != "series":
            raise MediaNotFoundError("Episode not found.")

        runtime = max(episode.runtime_minutes, 0)
        if mark_watched:
            episode.watched_minutes = runtime
        elif watched_minutes is not None:
            episode.watched_minutes = min(max(watched_minutes, 0), runtime if runtime > 0 else watched_minutes)

        episode.is_watched = runtime > 0 and episode.watched_minutes >= runtime
        await self.session.commit()
        await self.session.refresh(episode)
        return self._to_episode_card(episode)

    async def update_season_progress(
        self,
        season_id: UUID,
        tg_user_id: int,
        mark_watched: bool,
    ) -> MediaSeasonCardResponse:
        season = await self.media_repository.get_season(season_id)
        if season is None:
            raise MediaNotFoundError("Season not found.")

        series_item = await self.media_repository.get_item_by_id(season.series_item_id, tg_user_id)
        if series_item is None or series_item.media_type != "series":
            raise MediaNotFoundError("Season not found.")

        episodes = await self.media_repository.list_episodes(season.id)
        if mark_watched:
            for episode in episodes:
                runtime = max(episode.runtime_minutes, 0)
                episode.watched_minutes = runtime
                episode.is_watched = True

        await self._sync_series_watched_state(series_item)
        await self.session.commit()
        return self._to_season_card(season, episodes)

    async def update_series_progress(
        self,
        item_id: UUID,
        tg_user_id: int,
        mark_watched: bool,
    ) -> MediaCardResponse:
        item = await self._require_item(item_id, tg_user_id, "series")
        episodes = await self.media_repository.list_episodes_by_series_item(item.id)

        if mark_watched:
            for episode in episodes:
                runtime = max(episode.runtime_minutes, 0)
                episode.watched_minutes = runtime
                episode.is_watched = True

        await self._sync_series_watched_state(item, episodes)
        await self.session.commit()
        await self.session.refresh(item)
        return self._to_media_card(item)

    async def list_vocabulary_by_scope(self, tg_user_id: int, scope: str) -> list[VocabularyWordShortResponse]:
        if scope not in VALID_MEDIA_VOCAB_SCOPES:
            raise ValueError("Scope must be one of: movie, series, franchise.")
        words = await self.media_repository.list_words_by_scope(tg_user_id, scope)
        return self._to_word_short_list(words, scope)

    async def _add_movie(self, tg_user_id: int, tmdb_id: int) -> MediaItem:
        details = await self.tmdb_service.get_movie_details(tmdb_id)
        release_date = details.get("release_date")
        release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None
        movie_item = await self.media_repository.upsert_media_item(
            tg_user_id=tg_user_id,
            media_type="movie",
            tmdb_id=details["id"],
            title=details.get("title") or "Untitled",
            overview=details.get("overview"),
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            release_year=release_year,
            runtime_minutes=details.get("runtime") or 0,
        )

        collection = details.get("belongs_to_collection")
        if collection:
            franchise_item = await self.media_repository.upsert_media_item(
                tg_user_id=tg_user_id,
                media_type="franchise",
                tmdb_id=collection.get("id"),
                title=collection.get("name") or "Franchise",
                overview=None,
                poster_path=collection.get("poster_path"),
                backdrop_path=collection.get("backdrop_path"),
                release_year=release_year,
                runtime_minutes=0,
            )
            await self.media_repository.add_movie_to_franchise(franchise_item.id, movie_item.id, 0)

            collection_details = await self.tmdb_service.get_collection_details(collection.get("id"))
            for index, part in enumerate(collection_details.get("parts", [])):
                part_release_date = part.get("release_date")
                part_year = int(part_release_date[:4]) if part_release_date and len(part_release_date) >= 4 else None
                part_item = await self.media_repository.upsert_media_item(
                    tg_user_id=tg_user_id,
                    media_type="movie",
                    tmdb_id=part.get("id"),
                    title=part.get("title") or "Untitled",
                    overview=part.get("overview"),
                    poster_path=part.get("poster_path"),
                    backdrop_path=part.get("backdrop_path"),
                    release_year=part_year,
                    runtime_minutes=0,
                )
                await self.media_repository.add_movie_to_franchise(franchise_item.id, part_item.id, index + 1)

        return movie_item

    async def _add_series(self, tg_user_id: int, tmdb_id: int) -> MediaItem:
        details = await self.tmdb_service.get_tv_details(tmdb_id)
        first_air_date = details.get("first_air_date")
        release_year = int(first_air_date[:4]) if first_air_date and len(first_air_date) >= 4 else None
        episode_runtime = 0
        if details.get("episode_run_time"):
            episode_runtime = details["episode_run_time"][0] or 0

        series_item = await self.media_repository.upsert_media_item(
            tg_user_id=tg_user_id,
            media_type="series",
            tmdb_id=details["id"],
            title=details.get("name") or "Untitled",
            overview=details.get("overview"),
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            release_year=release_year,
            runtime_minutes=episode_runtime,
        )

        for season in details.get("seasons", []):
            season_number = season.get("season_number")
            if season_number is None:
                continue
            season_details = await self.tmdb_service.get_tv_season_details(details["id"], season_number)
            season_item = await self.media_repository.upsert_season(
                series_item_id=series_item.id,
                tmdb_season_id=season_details.get("id"),
                season_number=season_number,
                title=season_details.get("name") or f"Season {season_number}",
                overview=season_details.get("overview"),
                poster_path=season_details.get("poster_path"),
                episode_count=len(season_details.get("episodes", [])),
            )

            for episode in season_details.get("episodes", []):
                episode_runtime = episode.get("runtime") or 0
                await self.media_repository.upsert_episode(
                    series_item_id=series_item.id,
                    season_id=season_item.id,
                    tmdb_episode_id=episode.get("id"),
                    season_number=season_number,
                    episode_number=episode.get("episode_number") or 0,
                    title=episode.get("name") or f"Episode {episode.get('episode_number') or 0}",
                    overview=episode.get("overview"),
                    runtime_minutes=episode_runtime,
                )
        return series_item

    async def _require_item(self, item_id: UUID, tg_user_id: int, expected_type: str) -> MediaItem:
        item = await self.media_repository.get_item_by_id(item_id, tg_user_id)
        if item is None or item.media_type != expected_type:
            raise MediaNotFoundError("Media item not found.")
        return item

    async def _sync_series_watched_state(
        self,
        series_item: MediaItem,
        episodes: list[MediaEpisode] | None = None,
    ) -> None:
        episode_list = episodes if episodes is not None else await self.media_repository.list_episodes_by_series_item(series_item.id)
        if not episode_list:
            series_item.is_watched = False
            series_item.watched_minutes = 0
            return

        watched_count = sum(1 for episode in episode_list if episode.is_watched)
        total_runtime = sum(max(episode.runtime_minutes, 0) for episode in episode_list)
        watched_runtime = sum(max(episode.watched_minutes, 0) for episode in episode_list)
        series_item.is_watched = watched_count == len(episode_list)
        if total_runtime > 0:
            series_item.runtime_minutes = total_runtime
            series_item.watched_minutes = min(watched_runtime, total_runtime)
        else:
            series_item.runtime_minutes = len(episode_list)
            series_item.watched_minutes = watched_count

    @staticmethod
    def _progress_percent(watched_minutes: int, runtime_minutes: int) -> int:
        if runtime_minutes <= 0:
            return 0
        return round((watched_minutes / runtime_minutes) * 100)

    def _to_media_card(self, item: MediaItem) -> MediaCardResponse:
        return MediaCardResponse(
            id=item.id,
            tmdb_id=item.tmdb_id,
            media_type=item.media_type,
            title=item.title,
            year=item.release_year,
            poster_path=item.poster_path,
            overview=item.overview,
            runtime_minutes=item.runtime_minutes,
            watched_minutes=item.watched_minutes,
            watched_percent=self._progress_percent(item.watched_minutes, item.runtime_minutes),
            is_watched=item.is_watched,
        )

    def _to_season_card(self, season: MediaSeason, episodes: list[MediaEpisode]) -> MediaSeasonCardResponse:
        watched_count = sum(1 for episode in episodes if episode.is_watched)
        watched_percent = self._progress_percent(watched_count, len(episodes)) if episodes else 0
        return MediaSeasonCardResponse(
            id=season.id,
            season_number=season.season_number,
            title=season.title,
            overview=season.overview,
            episode_count=max(season.episode_count, len(episodes)),
            watched_episodes=watched_count,
            watched_percent=watched_percent,
        )

    def _to_episode_card(self, episode: MediaEpisode) -> MediaEpisodeCardResponse:
        return MediaEpisodeCardResponse(
            id=episode.id,
            season_number=episode.season_number,
            episode_number=episode.episode_number,
            title=episode.title,
            overview=episode.overview,
            runtime_minutes=episode.runtime_minutes,
            watched_minutes=episode.watched_minutes,
            watched_percent=self._progress_percent(episode.watched_minutes, episode.runtime_minutes),
            is_watched=episode.is_watched,
        )

    @staticmethod
    def _to_word_short_list(words: list, media_kind: str) -> list[VocabularyWordShortResponse]:
        deduped: dict[UUID, VocabularyWordShortResponse] = {}
        for word in words:
            if word.id in deduped:
                continue
            deduped[word.id] = VocabularyWordShortResponse(
                id=word.id,
                original_text=word.original_text,
                translation_ru=word.translation_ru,
                meaning_ru=word.meaning_ru,
                status=word.status,
                source_label=word.source_label,
                media_kind=media_kind,
            )
        return list(deduped.values())
