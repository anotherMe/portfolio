
import lib.repo.prices_repository as repo
from lib.database import read_from_db
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PriceDTO(BaseModel):
    instrument_id: int
    price: float
    date: Optional[datetime] = None

    class Config:
        from_attributes = True


def get_latest_prices_for_instrument_list(session, inst_ids: list[int]) -> list[PriceDTO]:

    results = repo.get_latest_prices_for_instrument_list(session, inst_ids)
    price_dtos = []
    for instrument_id, price, date in results:
        price_dtos.append(PriceDTO(instrument_id=instrument_id, price=read_from_db(price), date=date))
    return price_dtos