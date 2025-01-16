from pydantic import BaseModel, Field, constr
from datetime import datetime
from typing import Optional
from uuid import UUID


class CategoryCreate(BaseModel):
    name: constr(min_length=1)


class CategoryResponse(BaseModel):
    id: Optional[UUID] = Field(default=None)
    user_id: Optional[UUID] = Field(default=None)
    name: str
    created_at: Optional[datetime] = Field(default=None)
