from collections import deque
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from db.models import Position
from enums import TransactionType, TradeType
from repositories import positions_repository, trades_repository, transactions_repository
from services import prices_service
from schemas.portfolio import PositionSummary, PositionTotals
from utils import read_from_db
import logging

log = logging.getLogger(__name__)

# ----------------------------
# 🔹 Utility functions
# ----------------------------

def compute_position_closed(qty: int, closing_date: Optional[datetime]) -> str:
    if qty > 0:
        return str(qty)
    elif qty == 0 and closing_date is None:
        return "No open quantity"
    else:
        return "Closed on " + closing_date.strftime("%Y-%m-%d") if closing_date else "Closed"

def _apply_fifo(session: Session, positions: List[Position]) -> List[PositionSummary]:
    """
    Apply FIFO to trades of the same Instrument
    """
    if not positions:
        return []

    position_ids = [p.id for p in positions]
    instrument_ids = [p.instrument_id for p in positions]

    all_trades = trades_repository.get_trades_for_position_list(session, position_ids)
    all_transactions = transactions_repository.get_transactions_for_position_list(session, position_ids)
    latest_prices = prices_service.get_latest_prices_for_instrument_list(session, instrument_ids)

    position_dtos = []
    
    for position in positions:
        # Initialize DTO with basic info
        dto = PositionSummary(
            position_id=position.id,
            account_id=position.account_id,
            instrument_id=position.instrument_id if position.instrument else 0,
            instrument_name=position.instrument.name if position.instrument else "",
            instrument_isin=position.instrument.isin if position.instrument else "",
            instrument_ticker=position.instrument.ticker if position.instrument else "",
            instrument_currency=position.instrument.currency if position.instrument else ""
        )
        
        # --- Get latest price --- 
        latest_price_entry = next((p for p in latest_prices if p.instrument_id == dto.instrument_id), None)
        dto.latest_price = latest_price_entry.price if latest_price_entry else 0.0
        dto.latest_price_date = latest_price_entry.date if latest_price_entry else None

        # --- Get Trades for this position ---
        trades = [t for t in all_trades if t.position_id == position.id]

        # --- Compute transactions amount --- 
        for transaction in all_transactions: 
            if transaction.position_id == position.id:
                amount = read_from_db(transaction.amount)
                if transaction.type == TransactionType.DIVIDEND:
                    dto.transactions_amount += amount
                else:
                    dto.transactions_amount -= amount

        # --- Apply FIFO logic --- 
        fifo_queue = deque()
        
        for current_trade in trades:
            qty = current_trade.quantity
            price = read_from_db(current_trade.price)

            if current_trade.type == TradeType.BUY:
                # Add to queue
                fifo_queue.append({"qty": qty, "cost_per_unit": price})
                dto.total_invested += qty * price

                if len(fifo_queue) == 1 and not dto.opening_date:
                    dto.opening_date = current_trade.date

            else:  # Sell trade
                sell_qty = qty
                sell_price = price

                while sell_qty > 0 and fifo_queue:
                    oldest_lot = fifo_queue[0]
                    matched_qty = min(oldest_lot["qty"], sell_qty)

                    # Realized PnL from this matched chunk
                    dto.realized_pnl += matched_qty * (sell_price - oldest_lot["cost_per_unit"])

                    # Reduce quantities
                    oldest_lot["qty"] -= matched_qty
                    sell_qty -= matched_qty

                    # Remove lot if fully consumed
                    if oldest_lot["qty"] == 0:
                        fifo_queue.popleft()
                        dto.closing_date = current_trade.date

        # --- Compute remaining quantity and cost basis ---
        for lot in fifo_queue:
            dto.remaining_quantity += lot["qty"]
            dto.remaining_cost_basis += lot["qty"] * lot["cost_per_unit"]

        # --- PnL Calculations ---
        current_value = dto.remaining_quantity * dto.latest_price
        dto.unrealized_pnl = current_value - dto.remaining_cost_basis

        dto.realized_pnl_percent = (dto.realized_pnl / dto.total_invested * 100) if dto.total_invested > 0 else 0.0
        dto.unrealized_pnl_percent = (dto.unrealized_pnl / dto.remaining_cost_basis * 100) if dto.remaining_cost_basis > 0 else 0.0
        
        # Total PnL
        dto.pnl = dto.realized_pnl + dto.unrealized_pnl + dto.transactions_amount
        dto.pnl_percent = (dto.pnl / dto.total_invested) if dto.total_invested > 0 else 0.0
        
        # Status String
        dto.position_closed = compute_position_closed(dto.remaining_quantity, dto.closing_date)

        position_dtos.append(dto)

    return position_dtos

def get_positions_totals(session: Session, account_id: int = None, include_open: bool = True, include_closed: bool = True) -> List[PositionTotals]:
    positions = get_positions_summary(session, account_id=account_id, include_open=include_open, include_closed=include_closed)

    totals_by_currency: dict = {}
    for pos in positions:
        currency = pos.instrument_currency or "Unknown"
        if currency not in totals_by_currency:
            totals_by_currency[currency] = PositionTotals(currency=currency, symbol=currency, total_invested=0.0, total_pnl=0.0)
        totals_by_currency[currency].total_invested += pos.total_invested
        totals_by_currency[currency].total_pnl += pos.pnl

    return list(totals_by_currency.values())


def get_positions_summary(session: Session, account_id: int = None, include_closed: bool = True, include_open: bool = True) -> List[PositionSummary]:
    """
    Retrieve positions summary.
    """
    all_positions = positions_repository.get_all_positions(session, account_id)
    dtos = _apply_fifo(session, all_positions)

    filtered_dtos = []
    for dto in dtos:
        is_closed = (dto.remaining_quantity == 0 and dto.closing_date is not None)
        
        if is_closed and include_closed:
            filtered_dtos.append(dto)
        elif not is_closed and include_open:
            filtered_dtos.append(dto)
            
    # Sort by opening date (ascending)
    filtered_dtos.sort(key=lambda x: x.opening_date or datetime.min.replace(tzinfo=timezone.utc))
    
    return filtered_dtos
