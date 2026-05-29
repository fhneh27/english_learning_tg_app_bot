from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.music import MusicTrackSearchItemResponse
from app.services.music_catalog_service import MusicCatalogService


class MusicService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository | None = None,
        music_catalog_service: MusicCatalogService | None = None,
    ) -> None:
        self.session = session
        self.user_repository = user_repository or UserRepository(session)
        self.music_catalog_service = music_catalog_service or MusicCatalogService()

    async def search_tracks(self, tg_user_id: int, query: str, limit: int = 8) -> list[MusicTrackSearchItemResponse]:
        await self.user_repository.upsert_user(tg_user_id=tg_user_id)
        return await self.music_catalog_service.search_tracks(query=query, limit=limit)
