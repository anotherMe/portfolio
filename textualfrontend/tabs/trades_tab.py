from textual.app import ComposeResult
from textual import on, work
from textual.widgets import Button, DataTable
from textual.containers import Horizontal, Vertical

from schemas.trade import TradeRead
from api_service import get_trades
import api_service
from edit.position_edit import TradeActionsModal
from edit.trade_edit import TradeEdit
from widgets.confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


class TradesTab(Vertical):
    """The Trades tab content."""

    DEFAULT_CSS = """
    TradesTab #trades-toolbar {
        height: auto;
        align-horizontal: right;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield DataTable(id="trades_table", cursor_type="row")
        with Horizontal(id="trades-toolbar"):
            yield Button("+ Add Trade", id="btn-add-trade", variant="success")

    def on_mount(self) -> None:
        table = self.query_one("#trades_table", DataTable)
        table.add_columns("Date", "Type", "Qty", "Price", "Description")
        self._trades: dict[str, TradeRead] = {}
        self._selected: TradeRead | None = None
        self._fetch_data()

    # ── Data ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _fetch_data(self) -> None:
        try:
            trades = get_trades()
        except Exception as exc:
            log.error(f"Failed to load trades: {exc}")
            trades = []
        self.app.call_from_thread(self._populate, trades)

    def _populate(self, trades: list[TradeRead]) -> None:
        self._trades = {str(t.id): t for t in trades}
        self._selected = None
        table = self.query_one("#trades_table", DataTable)
        table.clear()
        for t in trades:
            table.add_row(
                t.date.strftime("%Y-%m-%d %H:%M"),
                t.type.value.upper(),
                str(t.quantity),
                f"{t.price:,.4f}",
                t.description or "",
                key=str(t.id),
            )

    # ── Row selection ──────────────────────────────────────────────────

    @on(DataTable.RowSelected, "#trades_table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        trade = self._trades.get(str(event.row_key.value)) if event.row_key else None
        if trade is None:
            return
        self._selected = trade
        self.app.push_screen(TradeActionsModal(trade), self._on_action)

    # ── Action callbacks ───────────────────────────────────────────────

    def _on_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(
                TradeEdit(self._selected.position_id, self._selected),
                self._on_saved,
            )
        elif action == "delete":
            trade = self._selected
            self.app.push_screen(
                ConfirmScreen(
                    f"Delete trade on {trade.date.strftime('%Y-%m-%d %H:%M')} "
                    f"({trade.type.value.upper()} {trade.quantity} @ {trade.price:,.4f})?"
                ),
                lambda confirmed: self._delete(trade.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete(self, trade_id: int) -> None:
        try:
            api_service.delete_trade(trade_id)
        except Exception as exc:
            log.error(f"Failed to delete trade {trade_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    @on(Button.Pressed, "#btn-add-trade")
    def on_add_trade(self) -> None:
        self.app.push_screen(TradeEdit(), self._on_saved)

    def _on_saved(self, result: TradeRead | None) -> None:
        if result is not None:
            self._fetch_data()
