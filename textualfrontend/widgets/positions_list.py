from textual.app import ComposeResult
from textual import work
from textual.widgets import DataTable
from textual.containers import Vertical

from api_service import get_positions
from .positions_filter import Filter
from .positions_details import PositionDetails
from .formatting import format_currency, format_currency_color, format_percent_color, format_date

import logging
log = logging.getLogger(__name__)


class PositionsList(Vertical):
    """Positions DataTable (top) and PositionDetails panel (bottom)."""

    def compose(self) -> ComposeResult:
        yield DataTable(id="positions_table", cursor_type="row")
        yield PositionDetails(id="position_details")

    def on_mount(self) -> None:
        self._positions: dict = {}
        table = self.query_one("#positions_table", DataTable)
        self.columns_to_show = [
            "instrument_name", "instrument_ticker",
            "opening_date", "total_invested", "latest_price",
            "remaining_quantity", "pnl",
            "pnl_percent", "closing_date"
        ]
        table.add_columns(*self.columns_to_show)
        self.refresh_table()

    @work(exclusive=True, thread=True)
    def refresh_table(self, account_id: int = None, filter: Filter = None) -> None:
        """Clear and repopulate the table filtered by account_id and optional filter."""
        try:
            table = self.query_one("#positions_table", DataTable)
            position_status = filter.position_status if filter else "all"
            positions = get_positions(
                account_id=account_id,
                include_open=(position_status in ["open", "all"]),
                include_closed=(position_status in ["closed", "all"]),
            )
            if filter:
                if filter.instrument_name:
                    positions = [p for p in positions if filter.instrument_name.lower() in p.instrument_name.lower()]
                if filter.ticker:
                    positions = [p for p in positions if filter.ticker.lower() in p.instrument_ticker.lower()]
                if filter.isin:
                    positions = [p for p in positions if filter.isin.lower() in p.instrument_isin.lower()]
            table.clear()
            if positions:
                self._populate_table(positions, table)
        except Exception as exc:
            log.error(f"Failed to load positions: {exc}")

    def _populate_table(self, positions, table) -> None:
        self._positions = {}
        for position in positions:
            self._positions[str(position.position_id)] = position

            row_data = position.model_dump(include=set(self.columns_to_show))
            row_data["opening_date"] = format_date(row_data["opening_date"])
            row_data["closing_date"] = format_date(row_data["closing_date"])
            row_data["pnl_percent"] = format_percent_color(row_data["pnl_percent"])
            row_data["total_invested"] = format_currency(row_data["total_invested"], position.instrument_currency)
            row_data["latest_price"] = format_currency(row_data["latest_price"], position.instrument_currency)
            row_data["pnl"] = format_currency_color(row_data["pnl"], position.instrument_currency)

            table.add_row(*[row_data[col] for col in self.columns_to_show], key=str(position.position_id))
