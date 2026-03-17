from pydantic import BaseModel, ConfigDict
from datetime import datetime

from enums import PriceGranularity


class OHLCVBase(BaseModel):
    instrument_id: int
    timestamp: datetime
    granularity: PriceGranularity
    open: int | None = None
    high: int | None = None
    low: int | None = None
    close: int | None = None
    volume: int | None = None


class OHLCVCreate(OHLCVBase):
    pass


class OHLCVRead(OHLCVBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
