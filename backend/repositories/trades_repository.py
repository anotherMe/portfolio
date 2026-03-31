from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import Trade, Position
from utils import write_to_db
from schemas.trade import TradeCreate, TradeUpdate

def get_all_trades(session: Session):
    return session.query(Trade).order_by(Trade.date).all()
    
def get_all_trades_by_account(session: Session, account_id: int):
    return (
        session.query(Trade)
        .join(Position, Trade.position_id == Position.id)
        .filter(Position.account_id == account_id)
        .order_by(Trade.date)
        .all()
    )

def get_trades_for_position_list(session: Session, position_ids: list[int]) -> list[Trade]:
    if not position_ids:
        return []
    
    trades = (
        session.query(Trade)
        .join(Position, Trade.position_id == Position.id)
        .filter(Position.id.in_(position_ids))
        .order_by(Trade.date)
        .all()
    )
    return trades

def add_trade(session: Session, account_id: int, instrument_id: int, date, trade_type, quantity, price, description=None):
    trade = Trade(
        account_id=account_id,
        instrument_id=instrument_id,
        date=date,
        type=trade_type,
        quantity=int(quantity),
        price=write_to_db(price),
        description=description,
    )
    session.add(trade)
    session.flush()
    return trade

def create_trade(session: Session, data: TradeCreate) -> Trade:
    trade = Trade(
        position_id=data.position_id,
        date=data.date,
        type=data.type.value,
        quantity=data.quantity,
        price=write_to_db(data.price),
        description=data.description,
    )
    session.add(trade)
    session.flush()
    return trade


def update_trade(session: Session, trade_id: int, data: TradeUpdate) -> Optional[Trade]:
    trade = session.get(Trade, trade_id)
    if not trade:
        return None
    if data.date is not None:
        trade.date = data.date
    if data.type is not None:
        trade.type = data.type.value
    if data.quantity is not None:
        trade.quantity = data.quantity
    if data.price is not None:
        trade.price = write_to_db(data.price)
    if data.description is not None:
        trade.description = data.description
    session.flush()
    return trade


def delete_trade(session: Session, trade_id: int):
    trade = session.get(Trade, trade_id)
    if trade:
        session.delete(trade)
        session.flush()
        return True
    return False
