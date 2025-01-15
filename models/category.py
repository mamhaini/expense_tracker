from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: Optional[UUID] = Field(default=None)
    user_id: Optional[UUID] = Field(default=None)
    name: str
    created_at: Optional[datetime] = Field(default=None)
