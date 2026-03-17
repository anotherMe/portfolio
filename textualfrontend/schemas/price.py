from pydantic import BaseModel, ConfigDict
from datetime import datetime

from enums import PriceGranularity


class PriceBase(BaseModel):
    instrument_id: int
    date: datetime
    price: int
    granularity: PriceGranularity


class PriceCreate(PriceBase):
    pass


class PriceRead(PriceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
