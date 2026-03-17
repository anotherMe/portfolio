from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from enums import TradeType


class TradeBase(BaseModel):
    position_id: int
    date: datetime
    type: TradeType
    quantity: int
    price: int
    description: Optional[str] = None


class TradeCreate(TradeBase):
    pass


class TradeRead(TradeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
