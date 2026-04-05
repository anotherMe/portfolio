from textual.app import ComposeResult
from textual import work
from textual.widgets import DataTable
from textual.containers import Vertical

from api_service import get_position_totals
from .formatting import format_currency, format_currency_color

import logging
log = logging.getLogger(__name__)


class PositionsTotals(Vertical):
    """Summary totals panel shown below the positions table."""

    DEFAULT_CSS = """
    PositionsTotals {
        height: auto;
        border-top: solid $primary;
    }
    PositionsTotals DataTable {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield DataTable(id="totals_table", cursor_type="none")

    def on_mount(self) -> None:
        table = self.query_one("#totals_table", DataTable)
        table.add_columns("Currency", "Total Invested", "Total PnL")

    @work(exclusive=True, thread=True)
    def refresh_totals(self, account_id: int = None, include_open: bool = True, include_closed: bool = True) -> None:
        try:
            totals = get_position_totals(
                account_id=account_id,
                include_open=include_open,
                include_closed=include_closed,
            )
            table = self.query_one("#totals_table", DataTable)
            table.clear()
            for t in totals:
                table.add_row(
                    t.currency,
                    format_currency(t.total_invested, t.currency),
                    format_currency_color(t.total_pnl, t.currency),
                )
        except Exception as exc:
            log.error(f"Failed to load position totals: {exc}")
