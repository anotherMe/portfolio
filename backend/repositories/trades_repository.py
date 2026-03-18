from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import Trade, Position
from utils import write_to_db

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

def delete_trade(session: Session, trade_id: int):
    trade = session.get(Trade, trade_id)
    if trade:
        session.delete(trade)
        session.flush()
        return True
    return False
