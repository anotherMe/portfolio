
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models import Instrument    
from typing import List

import logging

log = logging.getLogger(__name__)

def get_instruments(db: Session) -> List[Instrument]:
    """
    Retrieve all instruments.
    """
    stmt = select(Instrument)
    result = db.execute(stmt)
    return result.scalars().all()

def get_instrument_by_id(db: Session, instrument_id: int) -> Instrument:
    """
    Retrieve an instrument by ID.
    """
    stmt = select(Instrument).where(Instrument.id == instrument_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_instrument_by_ticker(db: Session, ticker: str) -> Instrument:
    """
    Retrieve an instrument by ticker.
    """
    stmt = select(Instrument).where(Instrument.ticker == ticker)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_instrument_by_isin(db: Session, isin: str) -> Instrument:
    """
    Retrieve an instrument by isin.
    """
    stmt = select(Instrument).where(Instrument.isin == isin)
    result = db.execute(stmt)
    return result.scalar_one_or_none()