from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import List
from datetime import datetime, timedelta

from pydantic import BaseModel

from db.deps import get_db
from services import yahoo_finance_service
from repositories.instruments_repository import get_instrument_by_id
from repositories.ohlcvs_repository import get_latest_timestamp

import json
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


class LoadFromFileRequest(BaseModel):
    file_path: str
    create_instrument: bool = True


@router.post("/load-from-json-file")
def load_prices_from_json_file(request: LoadFromFileRequest, session: Session = Depends(get_db)):
    """
    Parse a Yahoo Finance JSON file from a local path and load OHLCV data.
    """
    try:
        with open(request.file_path, "r") as f:
            parser = yahoo_finance_service.parse_json_file_into_yahoo_symbol(f)
        yahoo_finance_service.parse_file(session, parser, request.create_instrument)
        return {"success": True, "message": f"Loaded OHLCV data for {parser.symbol.ticker}"}
    except FileNotFoundError:
        return {"success": False, "message": f"File not found: {request.file_path}"}
    except yahoo_finance_service.PortfolioException as e:
        return {"success": False, "message": e.message}
    except Exception as e:
        return {"success": False, "message": str(e)}