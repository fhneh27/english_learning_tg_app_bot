from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import assert_matching_tg_user_id, get_authenticated_tg_user_id
from app.db.session import get_db_session
from app.schemas.media import (
    EpisodeDetailResponse,
    FranchiseDetailResponse,
    MediaAddRequest,
    MediaCardResponse,
    MediaEpisodeCardResponse,
    MediaLibraryResponse,
    MediaProgressUpdateRequest,
    MediaSearchRequest,
    MediaSearchResponse,
    MediaSeasonCardResponse,
    MediaVocabularyResponse,
    MovieDetailResponse,
    SeasonDetailResponse,
    SeriesDetailResponse,
)
from app.services.media_service import MediaNotFoundError, MediaService
from app.services.tmdb_service import TMDBServiceError

router = APIRouter()


@router.post("/search", response_model=MediaSearchResponse)
async def search_media(
    payload: MediaSearchRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaSearchResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        results = await service.search(tg_user_id, payload.query, payload.filter_type)
        return MediaSearchResponse(results=results)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TMDBServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="TMDB is unavailable right now.") from exc


@router.post("/library/add", response_model=MediaCardResponse, status_code=status.HTTP_201_CREATED)
async def add_media_to_library(
    payload: MediaAddRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaCardResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        return await service.add_to_library(tg_user_id, payload.tmdb_id, payload.media_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TMDBServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="TMDB is unavailable right now.") from exc


@router.get("/library", response_model=MediaLibraryResponse)
async def get_media_library(
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaLibraryResponse:
    service = MediaService(session)
    return await service.get_library(tg_user_id)


@router.get("/movies/{item_id}", response_model=MovieDetailResponse)
async def get_movie_detail(
    item_id: UUID,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MovieDetailResponse:
    service = MediaService(session)
    try:
        return await service.get_movie_detail(item_id, tg_user_id)
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/series/{item_id}", response_model=SeriesDetailResponse)
async def get_series_detail(
    item_id: UUID,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> SeriesDetailResponse:
    service = MediaService(session)
    try:
        return await service.get_series_detail(item_id, tg_user_id)
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/seasons/{season_id}", response_model=SeasonDetailResponse)
async def get_season_detail(
    season_id: UUID,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> SeasonDetailResponse:
    service = MediaService(session)
    try:
        return await service.get_season_detail(season_id, tg_user_id)
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/episodes/{episode_id}", response_model=EpisodeDetailResponse)
async def get_episode_detail(
    episode_id: UUID,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> EpisodeDetailResponse:
    service = MediaService(session)
    try:
        return await service.get_episode_detail(episode_id, tg_user_id)
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/franchises/{item_id}", response_model=FranchiseDetailResponse)
async def get_franchise_detail(
    item_id: UUID,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> FranchiseDetailResponse:
    service = MediaService(session)
    try:
        return await service.get_franchise_detail(item_id, tg_user_id)
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/movies/{item_id}/progress", response_model=MediaCardResponse)
async def update_movie_progress(
    item_id: UUID,
    payload: MediaProgressUpdateRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaCardResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        return await service.update_movie_progress(
            item_id=item_id,
            tg_user_id=tg_user_id,
            watched_minutes=payload.watched_minutes,
            mark_watched=payload.mark_watched,
        )
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/episodes/{episode_id}/progress", response_model=MediaEpisodeCardResponse)
async def update_episode_progress(
    episode_id: UUID,
    payload: MediaProgressUpdateRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaEpisodeCardResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        return await service.update_episode_progress(
            episode_id=episode_id,
            tg_user_id=tg_user_id,
            watched_minutes=payload.watched_minutes,
            mark_watched=payload.mark_watched,
        )
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/seasons/{season_id}/progress", response_model=MediaSeasonCardResponse)
async def update_season_progress(
    season_id: UUID,
    payload: MediaProgressUpdateRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaSeasonCardResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        return await service.update_season_progress(
            season_id=season_id,
            tg_user_id=tg_user_id,
            mark_watched=payload.mark_watched,
        )
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/series/{item_id}/progress", response_model=MediaCardResponse)
async def update_series_progress(
    item_id: UUID,
    payload: MediaProgressUpdateRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaCardResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    service = MediaService(session)
    try:
        return await service.update_series_progress(
            item_id=item_id,
            tg_user_id=tg_user_id,
            mark_watched=payload.mark_watched,
        )
    except MediaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/vocabulary", response_model=MediaVocabularyResponse)
async def get_media_vocabulary(
    scope: str = Query(...),
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> MediaVocabularyResponse:
    service = MediaService(session)
    try:
        words = await service.list_vocabulary_by_scope(tg_user_id, scope)
        return MediaVocabularyResponse(words=words)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
