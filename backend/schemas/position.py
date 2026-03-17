
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PositionBase(BaseModel):
    account_id: int
    instrument_id: int
    closed: bool = False
    closing_date: Optional[datetime] = None


class PositionCreate(PositionBase):
    pass


class PositionRead(PositionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
