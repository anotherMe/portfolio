from typing import Optional
from sqlalchemy.orm import Session
from schemas.trade import TradeRead, TradeCreate, TradeUpdate
from repositories import trades_repository
from utils import read_from_db

def get_trades(session: Session, account_id: int = None) -> list[TradeRead]:
    """Retrieve all trades and map them to read schemas."""
    if account_id is not None:
        trades = trades_repository.get_all_trades_by_account(session, account_id)
    else:
        trades = trades_repository.get_all_trades(session)

    result = []
    for t in trades:
        trade_data = TradeRead.model_validate(t)
        trade_data.price = read_from_db(t.price)
        result.append(trade_data)

    return result


def get_trades_by_position(session: Session, position_id: int) -> list[TradeRead]:
    """Retrieve all trades for a specific position."""
    trades = trades_repository.get_trades_for_position_list(session, [position_id])
    result = []
    for t in trades:
        trade_data = TradeRead.model_validate(t)
        trade_data.price = read_from_db(t.price)
        result.append(trade_data)
    return result


def create_trade(session: Session, data: TradeCreate) -> TradeRead:
    trade = trades_repository.create_trade(session, data)
    session.commit()
    result = TradeRead.model_validate(trade)
    result.price = read_from_db(trade.price)
    return result


def update_trade(session: Session, trade_id: int, data: TradeUpdate) -> Optional[TradeRead]:
    trade = trades_repository.update_trade(session, trade_id, data)
    if trade is None:
        return None
    session.commit()
    result = TradeRead.model_validate(trade)
    result.price = read_from_db(trade.price)
    return result


def delete_trade(session: Session, trade_id: int) -> bool:
    deleted = trades_repository.delete_trade(session, trade_id)
    if deleted:
        session.commit()
    return deleted
