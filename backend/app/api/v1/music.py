from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.music import MusicSearchRequest, MusicSearchResponse
from app.services.music_catalog_service import MusicCatalogServiceError
from app.services.music_service import MusicService

router = APIRouter()


@router.post("/search", response_model=MusicSearchResponse)
async def search_music_tracks(
    payload: MusicSearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> MusicSearchResponse:
    service = MusicService(session)
    try:
        results = await service.search_tracks(payload.tg_user_id, payload.query, payload.limit)
        return MusicSearchResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MusicCatalogServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
