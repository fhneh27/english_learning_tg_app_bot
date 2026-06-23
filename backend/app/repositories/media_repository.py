from uuid import UUID

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import MediaEpisode, MediaFranchiseMovie, MediaItem, MediaSeason
from app.models.vocabulary import VocabularyEntry


class MediaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_library_items(self, tg_user_id: int) -> list[MediaItem]:
        statement: Select[tuple[MediaItem]] = (
            select(MediaItem)
            .where(MediaItem.tg_user_id == tg_user_id)
            .order_by(MediaItem.title.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_item_by_id(self, item_id: UUID, tg_user_id: int) -> MediaItem | None:
        statement = select(MediaItem).where(
            MediaItem.id == item_id,
            MediaItem.tg_user_id == tg_user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_item_by_tmdb(self, tg_user_id: int, media_type: str, tmdb_id: int) -> MediaItem | None:
        statement = select(MediaItem).where(
            MediaItem.tg_user_id == tg_user_id,
            MediaItem.media_type == media_type,
            MediaItem.tmdb_id == tmdb_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert_media_item(
        self,
        tg_user_id: int,
        media_type: str,
        tmdb_id: int | None,
        title: str,
        overview: str | None,
        poster_path: str | None,
        backdrop_path: str | None,
        release_year: int | None,
        runtime_minutes: int,
    ) -> MediaItem:
        existing = None
        if tmdb_id is not None:
            existing = await self.get_item_by_tmdb(tg_user_id, media_type, tmdb_id)

        if existing is None:
            existing = MediaItem(
                tg_user_id=tg_user_id,
                media_type=media_type,
                tmdb_id=tmdb_id,
                title=title,
                overview=overview,
                poster_path=poster_path,
                backdrop_path=backdrop_path,
                release_year=release_year,
                runtime_minutes=max(runtime_minutes, 0),
                watched_minutes=0,
                is_watched=False,
            )
            self.session.add(existing)
        else:
            existing.title = title
            existing.overview = overview
            existing.poster_path = poster_path
            existing.backdrop_path = backdrop_path
            existing.release_year = release_year
            if runtime_minutes > 0:
                existing.runtime_minutes = runtime_minutes
                if existing.watched_minutes > existing.runtime_minutes:
                    existing.watched_minutes = existing.runtime_minutes
                    existing.is_watched = existing.watched_minutes >= existing.runtime_minutes

        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def list_seasons(self, series_item_id: UUID) -> list[MediaSeason]:
        statement = select(MediaSeason).where(MediaSeason.series_item_id == series_item_id).order_by(MediaSeason.season_number.asc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_season(self, season_id: UUID) -> MediaSeason | None:
        statement = select(MediaSeason).where(MediaSeason.id == season_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_season_by_number(self, series_item_id: UUID, season_number: int) -> MediaSeason | None:
        statement = select(MediaSeason).where(
            MediaSeason.series_item_id == series_item_id,
            MediaSeason.season_number == season_number,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert_season(
        self,
        series_item_id: UUID,
        tmdb_season_id: int | None,
        season_number: int,
        title: str,
        overview: str | None,
        poster_path: str | None,
        episode_count: int,
    ) -> MediaSeason:
        existing = await self.get_season_by_number(series_item_id, season_number)
        if existing is None:
            existing = MediaSeason(
                series_item_id=series_item_id,
                tmdb_season_id=tmdb_season_id,
                season_number=season_number,
                title=title,
                overview=overview,
                poster_path=poster_path,
                episode_count=max(episode_count, 0),
            )
            self.session.add(existing)
        else:
            existing.tmdb_season_id = tmdb_season_id
            existing.title = title
            existing.overview = overview
            existing.poster_path = poster_path
            existing.episode_count = max(episode_count, 0)

        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def list_episodes(self, season_id: UUID) -> list[MediaEpisode]:
        statement = select(MediaEpisode).where(MediaEpisode.season_id == season_id).order_by(MediaEpisode.episode_number.asc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_episodes_by_series_item(self, series_item_id: UUID) -> list[MediaEpisode]:
        statement = (
            select(MediaEpisode)
            .where(MediaEpisode.series_item_id == series_item_id)
            .order_by(MediaEpisode.season_number.asc(), MediaEpisode.episode_number.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_episode(self, episode_id: UUID) -> MediaEpisode | None:
        statement = select(MediaEpisode).where(MediaEpisode.id == episode_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_episode_by_number(self, season_id: UUID, episode_number: int) -> MediaEpisode | None:
        statement = select(MediaEpisode).where(
            MediaEpisode.season_id == season_id,
            MediaEpisode.episode_number == episode_number,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert_episode(
        self,
        series_item_id: UUID,
        season_id: UUID,
        tmdb_episode_id: int | None,
        season_number: int,
        episode_number: int,
        title: str,
        overview: str | None,
        runtime_minutes: int,
    ) -> MediaEpisode:
        existing = await self.get_episode_by_number(season_id, episode_number)
        if existing is None:
            existing = MediaEpisode(
                series_item_id=series_item_id,
                season_id=season_id,
                tmdb_episode_id=tmdb_episode_id,
                season_number=season_number,
                episode_number=episode_number,
                title=title,
                overview=overview,
                runtime_minutes=max(runtime_minutes, 0),
                watched_minutes=0,
                is_watched=False,
            )
            self.session.add(existing)
        else:
            existing.tmdb_episode_id = tmdb_episode_id
            existing.title = title
            existing.overview = overview
            if runtime_minutes > 0:
                existing.runtime_minutes = runtime_minutes
                if existing.watched_minutes > existing.runtime_minutes:
                    existing.watched_minutes = existing.runtime_minutes
                    existing.is_watched = existing.watched_minutes >= existing.runtime_minutes

        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def add_movie_to_franchise(self, franchise_item_id: UUID, movie_item_id: UUID, sort_order: int) -> None:
        statement = select(MediaFranchiseMovie).where(
            MediaFranchiseMovie.franchise_item_id == franchise_item_id,
            MediaFranchiseMovie.movie_item_id == movie_item_id,
        )
        result = await self.session.execute(statement)
        link = result.scalar_one_or_none()
        if link is None:
            link = MediaFranchiseMovie(
                franchise_item_id=franchise_item_id,
                movie_item_id=movie_item_id,
                sort_order=sort_order,
            )
            self.session.add(link)
        else:
            link.sort_order = sort_order
        await self.session.flush()

    async def list_franchise_movies(self, franchise_item_id: UUID) -> list[MediaItem]:
        statement = (
            select(MediaItem)
            .join(MediaFranchiseMovie, MediaFranchiseMovie.movie_item_id == MediaItem.id)
            .where(MediaFranchiseMovie.franchise_item_id == franchise_item_id)
            .order_by(MediaFranchiseMovie.sort_order.asc(), MediaItem.title.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_words_for_media_item(self, media_item_id: UUID, tg_user_id: int) -> list[VocabularyEntry]:
        statement = (
            select(VocabularyEntry)
            .where(
                VocabularyEntry.media_item_id == media_item_id,
                VocabularyEntry.tg_user_id == tg_user_id,
            )
            .order_by(VocabularyEntry.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_words_for_season(self, season_id: UUID, tg_user_id: int) -> list[VocabularyEntry]:
        statement = (
            select(VocabularyEntry)
            .where(
                VocabularyEntry.media_season_id == season_id,
                VocabularyEntry.tg_user_id == tg_user_id,
            )
            .order_by(VocabularyEntry.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_words_for_episode(self, episode_id: UUID, tg_user_id: int) -> list[VocabularyEntry]:
        statement = (
            select(VocabularyEntry)
            .where(
                VocabularyEntry.media_episode_id == episode_id,
                VocabularyEntry.tg_user_id == tg_user_id,
            )
            .order_by(VocabularyEntry.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_words_for_franchise(self, franchise_id: UUID, tg_user_id: int) -> list[VocabularyEntry]:
        statement = (
            select(VocabularyEntry)
            .where(
                VocabularyEntry.media_franchise_id == franchise_id,
                VocabularyEntry.tg_user_id == tg_user_id,
            )
            .order_by(VocabularyEntry.created_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_words_by_scope(self, tg_user_id: int, scope: str) -> list[VocabularyEntry]:
        base_query = select(VocabularyEntry).where(
            VocabularyEntry.tg_user_id == tg_user_id,
            VocabularyEntry.source_type == "media",
        )

        if scope == "movie":
            movie_ids_statement = select(MediaItem.id).where(
                MediaItem.tg_user_id == tg_user_id,
                MediaItem.media_type == "movie",
            )
            statement = base_query.where(VocabularyEntry.media_item_id.in_(movie_ids_statement))
        elif scope == "series":
            series_ids_statement = select(MediaItem.id).where(
                MediaItem.tg_user_id == tg_user_id,
                MediaItem.media_type == "series",
            )
            statement = base_query.where(
                or_(
                    VocabularyEntry.media_item_id.in_(series_ids_statement),
                    VocabularyEntry.media_episode_id.is_not(None),
                    VocabularyEntry.media_season_id.is_not(None),
                )
            )
        else:
            statement = base_query.where(VocabularyEntry.media_franchise_id.is_not(None))

        statement = statement.order_by(VocabularyEntry.created_at.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_episodes_by_user(self, tg_user_id: int) -> list[MediaEpisode]:
        statement = (
            select(MediaEpisode)
            .join(MediaItem, MediaItem.id == MediaEpisode.series_item_id)
            .where(MediaItem.tg_user_id == tg_user_id, MediaItem.media_type == "series")
            .order_by(MediaEpisode.updated_at.desc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
