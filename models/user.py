from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class UserCredentials(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
