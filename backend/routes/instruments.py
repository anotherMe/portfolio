
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import instruments_service
from schemas.instrument import InstrumentRead

router = APIRouter()

@router.get("/", response_model=List[InstrumentRead])
def get_instruments(session: Session = Depends(get_db)):
    """
    Retrieve the instruments.
    """
    return instruments_service.get_instruments(session)
