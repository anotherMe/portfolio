from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from lib.database import get_session, write_to_db
from lib.repo.accounts_repository import get_account_by_name
from lib.repo.instruments_repository import get_instrument_by_id, get_instrument_by_ticker
from lib.repo.trades_repository import add_trade as repo_add_trade, delete_trade as repo_delete_trade, get_trade_by_id
from lib.repo.positions_repository import get_position_by_id, close_position
from service.positions_service import get_positions_summary, get_positions_totals
from service.instruments_service import get_all_instruments
from service.transactions_service import get_all_transactions
from service.trades_service import get_all_trades
from service.accounts_service import get_all_accounts

app = FastAPI(title="PIP Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/api/positions")
def read_positions(
    account_name: Optional[str] = "All",
    status_filter: str = Query("all", description="all, open, or closed"),
    db = Depends(get_db)
):
    include_closed = status_filter in ("all", "closed")
    include_open = status_filter in ("all", "open")
    
    account = None
    if account_name and account_name.lower() != "all":
        account = get_account_by_name(db, account_name)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    positions = get_positions_summary(
        db, 
        account=account, 
        include_closed=include_closed, 
        include_open=include_open
    )
    
    return [p.model_dump() for p in positions]

@app.get("/api/positions/totals")
def read_positions_totals(
    account_name: Optional[str] = "All",
    status_filter: str = Query("all", description="all, open, or closed"),
    db = Depends(get_db)
):
    include_closed = status_filter in ("all", "closed")
    include_open = status_filter in ("all", "open")
    
    account = None
    if account_name and account_name.lower() != "all":
        account = get_account_by_name(db, account_name)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    totals = get_positions_totals(
        db, 
        account=account, 
        include_closed=include_closed, 
        include_open=include_open
    )
    
    return [t.model_dump() for t in totals]

@app.get("/api/instruments")
def read_instruments(db = Depends(get_db)):
    instruments = get_all_instruments(db)
    return [i.model_dump() for i in instruments]

@app.get("/api/transactions")
def read_transactions(
    account_name: Optional[str] = "All",
    db = Depends(get_db)
):
    account = None
    if account_name and account_name.lower() != "all":
        account = get_account_by_name(db, account_name)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    transactions = get_all_transactions(db, account=account)
    return [t.model_dump() for t in transactions]

@app.get("/api/trades")
def read_trades(
    account_name: Optional[str] = "All",
    db = Depends(get_db)
):
    account = None
    if account_name and account_name.lower() != "all":
        account = get_account_by_name(db, account_name)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    trades = get_all_trades(db, account=account)
    return [t.model_dump() for t in trades]

@app.get("/api/accounts")
def read_accounts(db = Depends(get_db)):
    accounts = get_all_accounts(db)
    return [a.model_dump() for a in accounts]


# -----------------------
# Request Models
# -----------------------

class TradeCreateRequest(BaseModel):
    account_name: str
    instrument_ticker: str
    date: datetime
    trade_type: str
    quantity: int
    price: float
    description: Optional[str] = None


class TradeUpdateRequest(BaseModel):
    date: datetime
    trade_type: str
    quantity: int
    price: float
    description: Optional[str] = None


class PositionCloseRequest(BaseModel):
    closing_date: datetime


# -----------------------
# Trade Endpoints
# -----------------------

@app.post("/api/trades", status_code=201)
def create_trade(request: TradeCreateRequest, db = Depends(get_db)):
    account = get_account_by_name(db, request.account_name)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    instrument = get_instrument_by_ticker(db, request.instrument_ticker)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    trade = repo_add_trade(
        db, 
        account, 
        instrument, 
        request.date, 
        request.trade_type, 
        request.quantity, 
        request.price, 
        request.description
    )
    db.commit()
    
    return {"id": trade.id, "message": "Trade created successfully"}


@app.put("/api/trades/{trade_id}")
def update_trade(trade_id: int, request: TradeUpdateRequest, db = Depends(get_db)):
    trade = get_trade_by_id(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    trade.date = request.date
    trade.type = request.trade_type
    trade.quantity = request.quantity
    trade.price = write_to_db(request.price)
    trade.description = request.description
    
    db.commit()
    return {"id": trade.id, "message": "Trade updated successfully"}


@app.delete("/api/trades/{trade_id}")
def delete_trade(trade_id: int, db = Depends(get_db)):
    success = repo_delete_trade(db, trade_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trade not found")
    db.commit()
    return {"message": "Trade deleted successfully"}


# -----------------------
# Position Endpoints
# -----------------------

@app.post("/api/positions/{position_id}/close")
def close_position_endpoint(position_id: int, request: PositionCloseRequest, db = Depends(get_db)):
    position = get_position_by_id(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    close_position(db, position, request.closing_date)
    db.commit()
    return {"id": position.id, "message": "Position closed successfully"}
