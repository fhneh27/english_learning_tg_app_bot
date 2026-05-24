from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegisterRequest, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    repository = UserRepository(session)
    await repository.upsert_user(
        tg_user_id=payload.tg_user_id,
        username=payload.username,
        first_name=payload.first_name,
    )
    await session.commit()
    created_or_updated = await repository.get_by_tg_user_id(payload.tg_user_id)
    if created_or_updated is None:
        raise RuntimeError("Registered user not found after commit.")
    await session.refresh(created_or_updated)
    return created_or_updated


@router.get("", response_model=list[UserResponse])
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[UserResponse]:
    repository = UserRepository(session)
    return await repository.list_users(limit=limit, offset=offset)
