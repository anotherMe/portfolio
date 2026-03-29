from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import List
from datetime import datetime, timedelta

from db.deps import get_db
from services import yahoo_finance_service
from repositories.instruments_repository import get_instrument_by_id
from repositories.ohlcvs_repository import get_latest_timestamp

import time

router = APIRouter()

@router.post("/load/{instrument_id}")
def load_prices_for_instrument(instrument_id: int, session: Session = Depends(get_db)):
    """
    Load prices for a specific instrument.
    """

    instrument = get_instrument_by_id(session, instrument_id)
    if not instrument:
        return {"success": False, "message": "Instrument not found"}

    last_date = get_latest_timestamp(session, instrument_id)
    if last_date:
        start_date = last_date
    else:
        start_date = datetime.now() - timedelta(days=365)  # If no data, load last year

    success, message = yahoo_finance_service.download_history(session, instrument, start_date)
    return {"success": success, "message": message}