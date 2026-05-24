from fastapi import APIRouter

from app.api.v1.users import router as users_router
from app.api.v1.vocabulary import router as vocabulary_router

api_router = APIRouter()


@api_router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(vocabulary_router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
