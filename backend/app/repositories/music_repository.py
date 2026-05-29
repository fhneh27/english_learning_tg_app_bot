from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.music import MusicTrack


class MusicRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_track_id(
        self,
        tg_user_id: int,
        provider: str,
        provider_track_id: str,
    ) -> MusicTrack | None:
        statement: Select[tuple[MusicTrack]] = select(MusicTrack).where(
            MusicTrack.tg_user_id == tg_user_id,
            MusicTrack.provider == provider,
            MusicTrack.provider_track_id == provider_track_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def upsert_track(
        self,
        *,
        tg_user_id: int,
        provider: str,
        provider_track_id: str,
        provider_release_id: str | None,
        title: str,
        artist_name: str,
        release_title: str | None,
        release_year: int | None,
        artwork_url: str | None,
        duration_ms: int | None,
    ) -> MusicTrack:
        existing = await self.get_by_provider_track_id(tg_user_id, provider, provider_track_id)
        if existing is None:
            existing = MusicTrack(
                tg_user_id=tg_user_id,
                provider=provider,
                provider_track_id=provider_track_id,
                provider_release_id=provider_release_id,
                title=title,
                artist_name=artist_name,
                release_title=release_title,
                release_year=release_year,
                artwork_url=artwork_url,
                duration_ms=duration_ms,
            )
            self.session.add(existing)
        else:
            existing.provider_release_id = provider_release_id
            existing.title = title
            existing.artist_name = artist_name
            existing.release_title = release_title
            existing.release_year = release_year
            existing.artwork_url = artwork_url
            existing.duration_ms = duration_ms

        await self.session.flush()
        await self.session.refresh(existing)
        return existing
