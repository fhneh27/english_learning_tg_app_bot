from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import assert_matching_tg_user_id, enforce_ai_rate_limit, get_authenticated_tg_user_id
from app.db.session import get_db_session
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    DailyVocabularySuggestionResponse,
    SuggestionBlacklistRequest,
    SuggestionBlacklistResponse,
    StreakSummaryResponse,
    UpdateAIInstructionsRequest,
    UpdateAIInstructionsResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.services.openai_service import OpenAIRateLimitError, OpenAIServiceError
from app.services.streak_service import StreakService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    repository = UserRepository(session)
    await repository.upsert_user(
        tg_user_id=tg_user_id,
        username=payload.username,
        first_name=payload.first_name,
    )
    await session.commit()
    created_or_updated = await repository.get_by_tg_user_id(tg_user_id)
    if created_or_updated is None:
        raise RuntimeError("Registered user not found after commit.")
    await session.refresh(created_or_updated)
    return created_or_updated


@router.get("/streak", response_model=StreakSummaryResponse)
async def get_user_streak(
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> StreakSummaryResponse:
    streak_service = StreakService(
        session=session,
        activity_repository=ActivityRepository(session),
        user_repository=UserRepository(session),
    )
    return await streak_service.get_summary(tg_user_id)


@router.get("/streak/suggestions", response_model=DailyVocabularySuggestionResponse)
async def get_streak_suggestions(
    tg_user_id: int = Depends(enforce_ai_rate_limit),
    session: AsyncSession = Depends(get_db_session),
) -> DailyVocabularySuggestionResponse:
    streak_service = StreakService(
        session=session,
        activity_repository=ActivityRepository(session),
        user_repository=UserRepository(session),
    )
    try:
        return await streak_service.get_daily_vocabulary_suggestions(tg_user_id)
    except OpenAIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI quota or rate limit reached. Please try again later.",
        ) from exc
    except OpenAIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI could not generate vocabulary suggestions right now.",
        ) from exc


@router.post("/streak/suggestions/blacklist", response_model=SuggestionBlacklistResponse)
async def add_suggestion_to_blacklist(
    payload: SuggestionBlacklistRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> SuggestionBlacklistResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    streak_service = StreakService(
        session=session,
        activity_repository=ActivityRepository(session),
        user_repository=UserRepository(session),
    )
    blacklist_size = await streak_service.add_suggestion_to_blacklist(tg_user_id, payload.text)
    return SuggestionBlacklistResponse(text=payload.text, blacklist_size=blacklist_size)


@router.post("/ai-instructions", response_model=UpdateAIInstructionsResponse)
async def update_ai_instructions(
    payload: UpdateAIInstructionsRequest,
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> UpdateAIInstructionsResponse:
    assert_matching_tg_user_id(payload.tg_user_id, tg_user_id)
    repository = UserRepository(session)
    user = await repository.update_ai_custom_instructions(tg_user_id, payload.ai_custom_instructions)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    await session.commit()
    await session.refresh(user)
    return UpdateAIInstructionsResponse(
        tg_user_id=user.tg_user_id,
        ai_custom_instructions=user.ai_custom_instructions,
        success=True,
    )


@router.get("/ai-instructions", response_model=UpdateAIInstructionsResponse)
async def get_ai_instructions(
    tg_user_id: int = Depends(get_authenticated_tg_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> UpdateAIInstructionsResponse:
    repository = UserRepository(session)
    user = await repository.get_by_tg_user_id(tg_user_id)
    if user is None:
        return UpdateAIInstructionsResponse(
            tg_user_id=tg_user_id,
            ai_custom_instructions=None,
            success=True,
        )
    return UpdateAIInstructionsResponse(
        tg_user_id=user.tg_user_id,
        ai_custom_instructions=user.ai_custom_instructions,
        success=True,
    )
