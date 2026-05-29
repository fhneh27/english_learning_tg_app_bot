from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.vocabulary import (
    VocabularyAnalysisResponse,
    VocabularyAnalyzeRequest,
    VocabularyCreateRequest,
    VocabularyEntryResponse,
    VocabularyFollowUpRequest,
    VocabularyFollowUpResponse,
    VocabularySaveRequest,
    VocabularyStatusUpdateRequest,
)
from app.services.openai_service import OpenAIRateLimitError, OpenAIServiceError
from app.services.vocabulary_service import EntryNotFoundError, VocabularyService

router = APIRouter()


@router.post("", response_model=VocabularyEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_vocabulary_entry(
    payload: VocabularyCreateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyEntryResponse:
    service = VocabularyService(session)
    try:
        return await service.create_entry(
            payload.tg_user_id,
            payload.text,
            payload.source_type,
            payload.analysis_mode,
            payload.media_item_id,
            payload.media_season_id,
            payload.media_episode_id,
            payload.media_franchise_id,
            payload.music_track_external_id,
            payload.music_release_external_id,
            payload.music_track_title,
            payload.music_artist_name,
            payload.music_release_title,
            payload.music_release_year,
            payload.music_artwork_url,
            payload.music_duration_ms,
            payload.source_label,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI quota/rate limit reached. Please try later or switch API key.",
        ) from exc
    except OpenAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI could not process the text right now. Please try again.",
        ) from exc


@router.post("/analyze", response_model=VocabularyAnalysisResponse)
async def analyze_vocabulary_entry(
    payload: VocabularyAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyAnalysisResponse:
    service = VocabularyService(session)
    try:
        analysis, ai_model = await service.analyze_text(payload.text, payload.analysis_mode)
        return VocabularyAnalysisResponse(
            analysis=analysis,
            ai_model=ai_model,
            analysis_mode=payload.analysis_mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI quota/rate limit reached. Please try later or switch API key.",
        ) from exc
    except OpenAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI could not process the text right now. Please try again.",
        ) from exc


@router.post("/save", response_model=VocabularyEntryResponse, status_code=status.HTTP_201_CREATED)
async def save_vocabulary_entry(
    payload: VocabularySaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyEntryResponse:
    service = VocabularyService(session)
    try:
        return await service.save_entry(
            payload.tg_user_id,
            payload.analysis,
            payload.source_type,
            payload.analysis_mode,
            payload.media_item_id,
            payload.media_season_id,
            payload.media_episode_id,
            payload.media_franchise_id,
            payload.music_track_external_id,
            payload.music_release_external_id,
            payload.music_track_title,
            payload.music_artist_name,
            payload.music_release_title,
            payload.music_release_year,
            payload.music_artwork_url,
            payload.music_duration_ms,
            payload.source_label,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[VocabularyEntryResponse])
async def list_vocabulary_entries(
    tg_user_id: int = Query(..., description="Telegram user ID"),
    q: str | None = Query(None, description="Search by original text or translation"),
    status_filter: str | None = Query(None, alias="status"),
    source_type: str | None = Query(None, alias="source_type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[VocabularyEntryResponse]:
    service = VocabularyService(session)
    try:
        return await service.list_entries(
            tg_user_id=tg_user_id,
            query=q,
            status=status_filter,
            source_type=source_type,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{entry_id}", response_model=VocabularyEntryResponse)
async def get_vocabulary_entry(
    entry_id: UUID,
    tg_user_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyEntryResponse:
    service = VocabularyService(session)
    try:
        return await service.get_entry(entry_id, tg_user_id)
    except EntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found.") from exc


@router.post("/{entry_id}/follow-up", response_model=VocabularyFollowUpResponse)
async def explain_vocabulary_entry(
    entry_id: UUID,
    payload: VocabularyFollowUpRequest,
    tg_user_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyFollowUpResponse:
    service = VocabularyService(session)
    try:
        return await service.explain_entry(entry_id, tg_user_id, payload.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found.") from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI quota/rate limit reached. Please try later or switch API key.",
        ) from exc
    except OpenAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI could not explain this entry right now. Please try again.",
        ) from exc


@router.patch("/{entry_id}", response_model=VocabularyEntryResponse)
async def update_vocabulary_entry_status(
    entry_id: UUID,
    payload: VocabularyStatusUpdateRequest,
    tg_user_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
) -> VocabularyEntryResponse:
    service = VocabularyService(session)
    try:
        return await service.update_progress(
            entry_id=entry_id,
            tg_user_id=tg_user_id,
            status=payload.status,
            increment_repetition=payload.increment_repetition,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found.") from exc


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vocabulary_entry(
    entry_id: UUID,
    tg_user_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    service = VocabularyService(session)
    try:
        await service.delete_entry(entry_id, tg_user_id)
    except EntryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found.") from exc
