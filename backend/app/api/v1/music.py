from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import assert_matching_tg_user_id, get_authenticated_tg_user_id
from app.db.session import get_db_session
from app.schemas.music import MusicSearchRequest, MusicSearchResponse
from app.services.music_catalog_service import MusicCatalogServiceError
from app.services.music_service import MusicService

router = APIRouter()


@router.post("/search", response_model=MusicSearchResponse)
async def search_music_tracks(
    payload: MusicSearchRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MusicSearchResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MusicService(session)
    try:
        results = await service.search_tracks(tg_user_id, payload.query, payload.limit)
        return MusicSearchResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MusicCatalogServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
