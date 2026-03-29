from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import positions_service
from schemas.portfolio import PositionSummary

router = APIRouter()

@router.get("/", response_model=List[PositionSummary])
def get_portfolio(account_id: int = None, include_open: bool = True, include_closed: bool = True, db: Session = Depends(get_db)):
    """
    Retrieve the portfolio summary (positions with FIFO PnL).
    """
    return positions_service.get_positions_summary(db, account_id=account_id, include_open=include_open, include_closed=include_closed)
