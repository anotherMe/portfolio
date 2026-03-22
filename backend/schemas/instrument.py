
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InstrumentBase(BaseModel):
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: str
    name_long: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    currency: str


class InstrumentCreate(InstrumentBase):
    pass


class InstrumentRead(InstrumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class InstrumentWithLastPrice(InstrumentRead):
    last_price_date: Optional[datetime] = None
