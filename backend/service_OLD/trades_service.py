from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from lib.repo.trades_repository import get_all_trades as repo_get_all_trades, get_all_trades_by_account as repo_get_all_trades_by_account


class TradeDTO(BaseModel):
    id: int
    date: datetime
    type: str
    quantity: int
    price: float
    description: Optional[str] = None
    position_id: int

    class Config:
        from_attributes = True


def get_all_trades(session: Session, account=None) -> list[TradeDTO]:
    if account:
        trades = repo_get_all_trades_by_account(session, account)
    else:
        trades = repo_get_all_trades(session)
    return [TradeDTO.model_validate(t) for t in trades]
