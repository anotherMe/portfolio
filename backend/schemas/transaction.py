from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from enums import TransactionType


class TransactionBase(BaseModel):
    account_id: int
    position_id: Optional[int] = None
    date: datetime
    type: TransactionType
    amount: float
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
