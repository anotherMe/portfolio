from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PositionSummary(BaseModel):
    """Data Transfer Object for Position summary with FIFO PnL."""
    position_id: int
    account_id: int = 0

    instrument_id: int = 0
    instrument_name: str = ""
    instrument_isin: str = ""
    instrument_ticker: str = ""

    opening_date: Optional[datetime] = None

    total_invested: float = 0.00
    
    latest_price: float = 0.00
    latest_price_date: Optional[datetime] = None
    
    transactions_amount: float = 0.00
    closing_date: Optional[datetime] = None
    remaining_quantity: int = 0
    remaining_cost_basis: float = 0.00
    
    realized_pnl: float = 0.00
    unrealized_pnl: float = 0.00
    realized_pnl_percent: float = 0.00
    unrealized_pnl_percent: float = 0.00
    
    pnl: float = 0.00        # Total PnL (Realized + Unrealized + Transactions)
    pnl_percent: float = 0.00
    
    position_closed: str = "" # Status string

    model_config = ConfigDict(from_attributes=True)
