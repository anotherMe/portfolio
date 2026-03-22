
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import instruments_service
from schemas.instrument import InstrumentRead, InstrumentWithLastPrice

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
