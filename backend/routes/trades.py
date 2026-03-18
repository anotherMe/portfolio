from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import trades_service
from schemas.trade import TradeRead

router = APIRouter()

@router.get("/", response_model=List[TradeRead])
def get_trades(account_id: int = None, session: Session = Depends(get_db)):
    """
    Retrieve trades. Optional account filter.
    """
    return trades_service.get_trades(session, account_id)
