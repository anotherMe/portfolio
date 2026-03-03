from collections import deque
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from lib.database import read_from_db
from lib.models import Position, UTCDateTime
from lib.repo.trades_repository import get_trades_for_position_list
from lib.repo.positions_repository import get_all_positions

from lib.repo.transactions_repository import get_transactions_for_position_list
from logging_config import setup_logger
from service import prices_service

log = setup_logger(__name__)


# -----------------------
# -- DTO Models
# -----------------------

class PositionDTO(BaseModel):
    model_config = ConfigDict(extra='allow', validate_assignment=False)
    
    position_id: int
    
    instrument_id: int = 0
    instrument_name: str = ""
    instrument_isin: str = ""
    instrument_ticker: str = ""
    instrument_currency: str = ""
    instrument_symbol: str = ""

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

    position_closed: str = ""
    pnl: float = 0.00
    pnl_percent: float = 0.00


class CurrencyTotalDTO(BaseModel):
    currency: str = ""
    symbol: str = ""
    total_invested: float = 0.00
    total_pnl: float = 0.00

def _apply_fifo(session, positions: list[Position]) -> list[PositionDTO]:
    """
    Apply FIFO to trades of the same Instrument
    Returns:
        closed_trades: list of dicts with realized PnL
        open_lots: remaining open lots (list of dicts)
    """

    all_trades = get_trades_for_position_list(session, [position.id for position in positions])
    all_transactions = get_transactions_for_position_list(session, [position.id for position in positions])
    latest_prices = prices_service.get_latest_prices_for_instrument_list(session, [position.instrument.id for position in positions])

    positionDTOs = []
    for position in positions:

        positionDTO = PositionDTO(position_id=position.id)
        positionDTO.instrument_id = position.instrument.id
        positionDTO.instrument_name = position.instrument.name
        positionDTO.instrument_isin = position.instrument.isin
        positionDTO.instrument_ticker = position.instrument.ticker
        positionDTO.instrument_currency = position.instrument.currency.name
        positionDTO.instrument_symbol = position.instrument.currency.symbol

        # --- Get latest price for this instrument --- 

        latest_price_entry = next((priceDTO for priceDTO in latest_prices if priceDTO.instrument_id == position.instrument.id), None)
        positionDTO.latest_price = latest_price_entry.price if latest_price_entry else 0.0
        positionDTO.latest_price_date = latest_price_entry.date if latest_price_entry else None


        # --- Get Trades for this position ---

        trades = [trade for trade in all_trades if trade.position_id == position.id]


        # --- Compute transactions amount --- 

        for transaction in all_transactions: 
            if transaction.position_id == position.id:
                if transaction.type in ('div'):
                    positionDTO.transactions_amount += read_from_db(transaction.amount)
                else:
                    positionDTO.transactions_amount -= read_from_db(transaction.amount)


        # --- Apply FIFO logic --- 

        fifo_queue: deque = deque()
        for current_trade in trades:

            qty = current_trade.quantity
            price = read_from_db(current_trade.price)

            if current_trade.type == "buy":
                
                fifo_queue.append({"qty": qty, "cost_per_unit": price})
                positionDTO.total_invested += qty * price

                if len(fifo_queue) == 1:  # First Buy trade sets the opening date
                    positionDTO.opening_date = current_trade.date

            else:  # Sell trade

                sell_qty = qty
                sell_price = price

                while sell_qty > 0 and fifo_queue:

                    oldest_lot = fifo_queue[0]
                    matched_qty = min(oldest_lot["qty"], sell_qty)

                    # Realized PnL from this matched chunk
                    positionDTO.realized_pnl += matched_qty * (sell_price - oldest_lot["cost_per_unit"])

                    # Reduce quantities
                    oldest_lot["qty"] -= matched_qty
                    sell_qty -= matched_qty


                    # Remove lot if fully consumed
                    if oldest_lot["qty"] == 0:
                        fifo_queue.popleft()
                        positionDTO.closing_date = current_trade.date  # update closing date only when a lot is fully sold


        # --- Compute remaining quantity and cost basis ---

        for lot in fifo_queue:
            positionDTO.remaining_quantity += lot["qty"]
            positionDTO.remaining_cost_basis += lot["qty"] * lot["cost_per_unit"]


        # --- PnL Calculations ---

        current_value = positionDTO.remaining_quantity * positionDTO.latest_price
        positionDTO.unrealized_pnl = current_value - positionDTO.remaining_cost_basis

        positionDTO.realized_pnl_percent = (positionDTO.realized_pnl / positionDTO.total_invested * 100) if positionDTO.total_invested > 0 else 0.0
        positionDTO.unrealized_pnl_percent = (positionDTO.unrealized_pnl / positionDTO.remaining_cost_basis * 100) if positionDTO.remaining_cost_basis > 0 else 0.0


        positionDTOs.append(positionDTO)

    return positionDTOs


def get_positions_summary(session, account=None, include_closed=True, include_open=True):
    """
    Retrieve positions summary as a list of PositionDTO models.
    """

    all_positions = get_all_positions(session, account)
    positionsDTO = _apply_fifo(session, all_positions)

    filtered_position_DTOs = []
    for pos in positionsDTO:
        if pos.closing_date and include_closed:
            filtered_position_DTOs.append(pos)
        elif not pos.closing_date and include_open:
            filtered_position_DTOs.append(pos)

    # Compute derived properties
    for pos in filtered_position_DTOs:
        if pos.remaining_quantity > 0:
            pos.position_closed = str(pos.remaining_quantity)
        elif pos.remaining_quantity == 0 and not pos.closing_date:
            pos.position_closed = "No open quantity"
        else:
            pos.position_closed = "Closed on " + pos.closing_date.strftime("%Y-%m-%d")

        pos.pnl = pos.realized_pnl + pos.unrealized_pnl + pos.transactions_amount
        pos.pnl_percent = (pos.pnl / pos.total_invested) if pos.total_invested > 0 else 0.0

    # Sort
    filtered_position_DTOs.sort(key=lambda x: x.opening_date.timestamp() if x.opening_date else 0.0)

    return filtered_position_DTOs

def get_position_summary(session, position: Position):
    """
        Retrieve positions summary as a pandas DataFrame.
    """

    positionDTOs = _apply_fifo(session, [position])

    p = positionDTOs[0]

    # p.pnl = p.realized_pnl + p.unrealized_pnl
    p.pnl = p.realized_pnl + p.unrealized_pnl + p.transactions_amount
    p.pnl_percent = ( p.pnl / p.total_invested ) if p.total_invested > 0 else 0.0

    return p


def get_positions_totals(session, account=None, include_closed=True, include_open=True):
    """
    Retrieve positions totals grouped by currency.
    """
    positions = get_positions_summary(
        session, 
        account=account, 
        include_closed=include_closed, 
        include_open=include_open
    )
    
    totals_map = {}
    for pos in positions:
        curr = pos.instrument_currency
        if curr not in totals_map:
            totals_map[curr] = CurrencyTotalDTO(
                currency=curr,
                symbol=pos.instrument_symbol,
                total_invested=0.0,
                total_pnl=0.0
            )
        
        totals_map[curr].total_invested += pos.total_invested
        totals_map[curr].total_pnl += pos.pnl
    
    return list(totals_map.values())