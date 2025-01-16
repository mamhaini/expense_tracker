from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"


class PaymentMethodEnum(str, Enum):
    BANK = "bank"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    payment_method: Optional[PaymentMethodEnum] = PaymentMethodEnum.BANK
    is_recurring: Optional[bool] = None
    currency: Optional[CurrencyEnum] = CurrencyEnum.USD


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[PaymentMethodEnum] = None
    is_recurring: Optional[bool] = None
    currency: Optional[CurrencyEnum] = None


class ExpenseResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    category: str
    description: Optional[str]
    payment_method: Optional[PaymentMethodEnum] = PaymentMethodEnum.BANK
    is_recurring: Optional[bool]
    currency: Optional[CurrencyEnum] = CurrencyEnum.USD
    created_at: datetime
    updated_at: Optional[datetime] = None
