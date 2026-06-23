from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.media import router as media_router
from app.api.v1.music import router as music_router
from app.api.v1.users import router as users_router
from app.api.v1.vocabulary import router as vocabulary_router
from app.db.session import get_db_session

api_router = APIRouter()


@api_router.get("/health")
async def healthcheck(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    return {"status": "ok", "database": "ok"}


api_router.include_router(vocabulary_router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(music_router, prefix="/music", tags=["music"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
