
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models import Instrument
from typing import List, Optional
from schemas.instrument import InstrumentCreate, InstrumentUpdate

import logging

log = logging.getLogger(__name__)

def create_instrument(session: Session, data: InstrumentCreate) -> Instrument:
    instrument = Instrument(**data.model_dump())
    session.add(instrument)
    session.flush()
    return instrument


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


def update_instrument(session: Session, instrument_id: int, data: InstrumentUpdate) -> Optional[Instrument]:
    instrument = session.get(Instrument, instrument_id)
    if not instrument:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(instrument, field, value)
    session.flush()
    return instrument


def delete_instrument(session: Session, instrument_id: int) -> bool:
    instrument = session.get(Instrument, instrument_id)
    if instrument:
        session.delete(instrument)
        session.flush()
        return True
    return False