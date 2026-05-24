from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRegisterRequest(BaseModel):
    tg_user_id: int
    username: str | None = Field(default=None, max_length=64)
    first_name: str | None = Field(default=None, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tg_user_id: int
    username: str | None
    first_name: str | None
    created_at: datetime
    updated_at: datetime
