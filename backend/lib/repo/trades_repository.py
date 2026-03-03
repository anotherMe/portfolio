
from lib.database import write_to_db, read_from_db
from lib.models import Trade
from sqlalchemy.orm import Session
from lib.models import Position


def _apply_conversions(trade):
    trade.price = read_from_db(trade.price)
    return trade


def get_all_trades(session):
    trades = session.query(Trade).order_by(Trade.date).all()
    return [_apply_conversions(t) for t in trades]
    
def get_all_trades_by_account(session, account):
    trades = session.query(Trade).join(Position).filter(Position.account_id == account.id).order_by(Trade.date).all()
    return [_apply_conversions(t) for t in trades]

def get_trades_for_position_list(session: Session, position_ids: list[int]) -> list[Trade]:
    
    trades = (
        session.query(Trade)
        .join(Position, Trade.position_id == Position.id)
        .filter(Position.id.in_(position_ids))
        .order_by(Trade.date)
        .all()
    )
    return trades

def get_trade_by_id(session, trade_id):
    trade = session.get(Trade, trade_id)
    if trade:
        trade.price = read_from_db(trade.price)
    return trade

def add_trade(session, account, instrument, date, trade_type, quantity, price, description=None):
    
    # Find active position for this account and instrument
    position = session.query(Position).filter_by(
        account_id=account.id, 
        instrument_id=instrument.id, 
        closed=False
    ).first()
    
    if not position:
        position = Position(
            account_id=account.id,
            instrument_id=instrument.id,
            closed=False
        )
        session.add(position)
        session.flush()

    trade = Trade(
        position_id=position.id,
        date=date,
        type=trade_type,
        quantity=int(quantity),
        price=write_to_db(price),
        description=description,
    )
    session.add(trade)
    session.flush()  # ensures IDs and defaults are populated

    print(f"📈 Recorded trade: {trade_type.upper()} {quantity}x {instrument.ticker or instrument.name} @ {price:.2f}")

    return trade

def delete_trade(session, trade_id):
    trade = session.get(Trade, trade_id)
    if trade:
        session.delete(trade)
        session.flush()
        print(f"🗑️ Deleted trade ID {trade_id}")
        return True
    else:
        print(f"❌ Trade ID {trade_id} not found.")
        return False
