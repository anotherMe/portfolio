from sqlalchemy.orm import Session
from schemas.trade import TradeRead
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
