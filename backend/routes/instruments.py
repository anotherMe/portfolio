
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import instruments_service
from schemas.instrument import InstrumentRead, InstrumentUpdate, InstrumentWithLastPrice

router = APIRouter()

@router.get("/", response_model=List[InstrumentRead])
def get_instruments(session: Session = Depends(get_db)):
    """
    Retrieve the instruments.
    """
    return instruments_service.get_instruments(session)


@router.get("/with-last-price", response_model=List[InstrumentWithLastPrice])
def get_instruments_with_last_price(session: Session = Depends(get_db)):
    """
    Retrieve the instruments with last price date.
    """
    return instruments_service.get_instruments_with_last_price(session)


@router.put("/{instrument_id}", response_model=InstrumentRead)
def update_instrument(instrument_id: int, data: InstrumentUpdate, session: Session = Depends(get_db)):
    result = instruments_service.update_instrument(session, instrument_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return result


@router.delete("/{instrument_id}", status_code=204)
def delete_instrument(instrument_id: int, session: Session = Depends(get_db)):
    deleted = instruments_service.delete_instrument(session, instrument_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Instrument not found")
