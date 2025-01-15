from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    category: str
    description: Optional[str]
    created_at: datetime
