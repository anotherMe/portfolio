from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.deps import get_db
from services import trades_service
from schemas.trade import TradeRead, TradeCreate, TradeUpdate

router = APIRouter()

@router.get("/", response_model=List[TradeRead])
def get_trades(account_id: int = None, position_id: int = None, session: Session = Depends(get_db)):
    """
    Retrieve trades. Optional account or position filter.
    """
    if position_id is not None:
        return trades_service.get_trades_by_position(session, position_id)
    return trades_service.get_trades(session, account_id)


@router.post("/", response_model=TradeRead, status_code=201)
def create_trade(data: TradeCreate, session: Session = Depends(get_db)):
    return trades_service.create_trade(session, data)


@router.put("/{trade_id}", response_model=TradeRead)
def update_trade(trade_id: int, data: TradeUpdate, session: Session = Depends(get_db)):
    result = trades_service.update_trade(session, trade_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return result


@router.delete("/{trade_id}", status_code=204)
def delete_trade(trade_id: int, session: Session = Depends(get_db)):
    deleted = trades_service.delete_trade(session, trade_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trade not found")
