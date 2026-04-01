from textual.app import ComposeResult
from textual import on, work
from textual.screen import ModalScreen
from textual.widgets import DataTable, Button, Static
from textual.containers import Vertical, Horizontal

from schemas.portfolio import PositionSummary
from schemas.trade import TradeRead
from schemas.transaction import TransactionRead
from api_service import get_trades_for_position, get_transactions_for_position
import api_service
from edit.trade_edit import TradeEdit
from edit.transaction_edit import TransactionEdit
from widgets.confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Row-action modals
# ──────────────────────────────────────────────────────────────────────────────

class TradeActionsModal(ModalScreen):
    """Modal shown when a trade row is selected."""

    BINDINGS = [("escape", "dismiss", "Cancel")]

    DEFAULT_CSS = """
    TradeActionsModal {
        align: center middle;
    }
    TradeActionsModal > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }
    TradeActionsModal #modal-info {
        padding-bottom: 1;
    }
    TradeActionsModal #modal-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    TradeActionsModal #modal-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, trade: TradeRead, **kwargs):
        super().__init__(**kwargs)
        self._trade = trade

    def compose(self) -> ComposeResult:
        t = self._trade
        with Vertical():
            yield Static(
                f"[bold]{t.date.strftime('%Y-%m-%d %H:%M')}[/bold]  "
                f"{t.type.value.upper()}  "
                f"Qty: [bold]{t.quantity}[/bold]  "
                f"@ [bold]{t.price:,.4f}[/bold]",
                id="modal-info",
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Cancel", id="modal-cancel-btn")
                yield Button("Edit", id="modal-edit-btn", variant="warning")
                yield Button("Delete", id="modal-delete-btn", variant="error")

    @on(Button.Pressed, "#modal-cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#modal-edit-btn")
    def on_edit(self) -> None:
        self.dismiss("edit")

    @on(Button.Pressed, "#modal-delete-btn")
    def on_delete(self) -> None:
        self.dismiss("delete")


class TransactionActionsModal(ModalScreen):
    """Modal shown when a transaction row is selected."""

    BINDINGS = [("escape", "dismiss", "Cancel")]

    DEFAULT_CSS = """
    TransactionActionsModal {
        align: center middle;
    }
    TransactionActionsModal > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }
    TransactionActionsModal #modal-info {
        padding-bottom: 1;
    }
    TransactionActionsModal #modal-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    TransactionActionsModal #modal-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, transaction: TransactionRead, **kwargs):
        super().__init__(**kwargs)
        self._transaction = transaction

    def compose(self) -> ComposeResult:
        tx = self._transaction
        with Vertical():
            yield Static(
                f"[bold]{tx.date.strftime('%Y-%m-%d %H:%M')}[/bold]  "
                f"{tx.type.value.upper()}  "
                f"Amount: [bold]{tx.amount:,.2f}[/bold]",
                id="modal-info",
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Cancel", id="modal-cancel-btn")
                yield Button("Edit", id="modal-edit-btn", variant="warning")
                yield Button("Delete", id="modal-delete-btn", variant="error")

    @on(Button.Pressed, "#modal-cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#modal-edit-btn")
    def on_edit(self) -> None:
        self.dismiss("edit")

    @on(Button.Pressed, "#modal-delete-btn")
    def on_delete(self) -> None:
        self.dismiss("delete")


# ──────────────────────────────────────────────────────────────────────────────
# Main widget
# ──────────────────────────────────────────────────────────────────────────────

class PositionEdit(Vertical):
    """
    Full-screen position editing widget.

    Shows instrument info, position P&L summary, and two side-by-side
    DataTables for trades and transactions. Selecting a row opens a modal
    with Edit and Delete actions. Add-new buttons are always visible.
    """

    DEFAULT_CSS = """
    PositionEdit {
        height: 1fr;
    }

    /* ── Header bars ─────────────────────────────────────────────── */
    #pe-instrument-bar {
        height: auto;
        padding: 0 2;
        background: $surface;
        border-bottom: solid $primary-darken-2;
    }
    #pe-instrument-bar Static {
        height: auto;
        padding: 0 1;
    }
    #pe-summary-bar {
        height: auto;
        padding: 0 2;
        background: $surface-darken-1;
        border-bottom: solid $primary-darken-2;
    }

    /* ── Tables section ──────────────────────────────────────────── */
    #pe-tables-section {
        height: 1fr;
    }
    #pe-trades-section {
        width: 1fr;
        border-right: solid $primary-darken-3;
    }
    #pe-transactions-section {
        width: 1fr;
    }
    .pe-section-title {
        height: 1;
        padding: 0 1;
        background: $primary-darken-2;
        color: $text;
        text-style: bold;
    }
    #pe-trades-table {
        height: 1fr;
    }
    #pe-transactions-table {
        height: 1fr;
    }

    /* ── Add / footer buttons ────────────────────────────────────── */
    .pe-add-bar {
        height: auto;
        padding: 1 1 1 1;
        margin-top: 1;
        align-horizontal: right;
        border-top: solid $primary-darken-3;
    }
    .pe-add-btn {
        width: auto;
    }
    #pe-footer {
        height: auto;
        padding: 1 2;
        border-top: solid $primary-darken-2;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._position: PositionSummary | None = None
        self._selected_trade: TradeRead | None = None
        self._selected_transaction: TransactionRead | None = None
        self._trades: dict[str, TradeRead] = {}
        self._transactions: dict[str, TransactionRead] = {}

    # ──────────────────────────────────────────────────────────────────
    # Composition
    # ──────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        # Instrument header
        with Horizontal(id="pe-instrument-bar"):
            yield Static("", id="pe-instrument-name")
            yield Static("", id="pe-instrument-meta")

        # Position P&L summary bar
        with Horizontal(id="pe-summary-bar"):
            yield Static("", id="pe-summary-info")

        # Main content: trades | transactions
        with Horizontal(id="pe-tables-section"):

            with Vertical(id="pe-trades-section"):
                yield Static("Trades", classes="pe-section-title")
                yield DataTable(id="pe-trades-table", cursor_type="row")
                with Horizontal(classes="pe-add-bar"):
                    yield Button("+ Add Trade", id="pe-add-trade-btn", variant="success", classes="pe-add-btn")

            with Vertical(id="pe-transactions-section"):
                yield Static("Transactions", classes="pe-section-title")
                yield DataTable(id="pe-transactions-table", cursor_type="row")
                with Horizontal(classes="pe-add-bar"):
                    yield Button("+ Add Transaction", id="pe-add-transaction-btn", variant="success", classes="pe-add-btn")

        # Footer
        with Horizontal(id="pe-footer"):
            yield Button("← Back to List", id="position-back-button", variant="primary")  # Note: This button is handled in positions_tab.py

    def on_mount(self) -> None:
        trades_table = self.query_one("#pe-trades-table", DataTable)
        trades_table.add_columns("Date", "Type", "Qty", "Price", "Description")

        transactions_table = self.query_one("#pe-transactions-table", DataTable)
        transactions_table.add_columns("Date", "Type", "Amount", "Description")

    def on_show(self) -> None:
        self.query_one("#pe-trades-table", DataTable).focus()
        

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def load(self, position: PositionSummary) -> None:
        """Load (or reload) data for the given position."""
        self._position = position
        self._update_header()
        self._fetch_data()

    # ──────────────────────────────────────────────────────────────────
    # Header rendering
    # ──────────────────────────────────────────────────────────────────

    def _update_header(self) -> None:
        p = self._position
        self.query_one("#pe-instrument-name", Static).update(
            f"[bold]{p.instrument_name}[/bold]  "
            f"[dim]{p.instrument_ticker}[/dim]  "
            f"[dim]{p.instrument_isin}[/dim]"
        )
        opening = p.opening_date.strftime("%Y-%m-%d") if p.opening_date else "—"
        closing = p.closing_date.strftime("%Y-%m-%d") if p.closing_date else "open"
        self.query_one("#pe-instrument-meta", Static).update(
            f"[dim]Position #{p.position_id}  |  {opening} → {closing}[/dim]"
        )

        pnl_color = "green" if p.pnl >= 0 else "red"
        pnl_sign = "+" if p.pnl >= 0 else ""
        self.query_one("#pe-summary-info", Static).update(
            f"Invested: [bold]{p.total_invested:,.2f}[/bold]"
            f"  Qty: [bold]{p.remaining_quantity}[/bold]"
            f"  Cost Basis: [bold]{p.remaining_cost_basis:,.2f}[/bold]"
            f"  Latest Price: [bold]{p.latest_price:,.4f}[/bold]"
            f"  PnL: [{pnl_color}]{pnl_sign}{p.pnl:,.2f} ({p.pnl_percent:.1%})[/{pnl_color}]"
            f"  Realized: [{pnl_color}]{p.realized_pnl:,.2f}[/{pnl_color}]"
            f"  Unrealized: [{pnl_color}]{p.unrealized_pnl:,.2f}[/{pnl_color}]"
        )

    # ──────────────────────────────────────────────────────────────────
    # Data loading (background thread)
    # ──────────────────────────────────────────────────────────────────

    @work(thread=True)
    def _fetch_data(self) -> None:
        position_id = self._position.position_id
        try:
            trades = get_trades_for_position(position_id)
        except Exception as exc:
            log.error(f"Failed to load trades for position {position_id}: {exc}")
            trades = []
        try:
            transactions = get_transactions_for_position(position_id)
        except Exception as exc:
            log.error(f"Failed to load transactions for position {position_id}: {exc}")
            transactions = []

        self.app.call_from_thread(self._populate_trades, trades)
        self.app.call_from_thread(self._populate_transactions, transactions)

    def _populate_trades(self, trades: list[TradeRead]) -> None:
        self._trades = {str(t.id): t for t in trades}
        self._selected_trade = None
        table = self.query_one("#pe-trades-table", DataTable)
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

    def _populate_transactions(self, transactions: list[TransactionRead]) -> None:
        self._transactions = {str(t.id): t for t in transactions}
        self._selected_transaction = None
        table = self.query_one("#pe-transactions-table", DataTable)
        table.clear()
        for t in transactions:
            table.add_row(
                t.date.strftime("%Y-%m-%d %H:%M"),
                t.type.value.upper(),
                f"{t.amount:,.2f}",
                t.description or "",
                key=str(t.id),
            )

    # ──────────────────────────────────────────────────────────────────
    # Row selection → open action modal
    # ──────────────────────────────────────────────────────────────────

    @on(DataTable.RowSelected, "#pe-trades-table")
    def on_trade_row_selected(self, event: DataTable.RowSelected) -> None:
        trade = self._trades.get(str(event.row_key.value)) if event.row_key else None
        if trade is None:
            return
        self._selected_trade = trade
        self.app.push_screen(TradeActionsModal(trade), self._on_trade_action)

    @on(DataTable.RowSelected, "#pe-transactions-table")
    def on_transaction_row_selected(self, event: DataTable.RowSelected) -> None:
        tx = self._transactions.get(str(event.row_key.value)) if event.row_key else None
        if tx is None:
            return
        self._selected_transaction = tx
        self.app.push_screen(TransactionActionsModal(tx), self._on_transaction_action)

    # ──────────────────────────────────────────────────────────────────
    # Trade button handlers
    # ──────────────────────────────────────────────────────────────────

    @on(Button.Pressed, "#pe-add-trade-btn")
    def on_add_trade(self) -> None:
        self.app.push_screen(
            TradeEdit(self._position.position_id),
            self._on_trade_saved,
        )

    def _on_trade_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(
                TradeEdit(self._position.position_id, self._selected_trade),
                self._on_trade_saved,
            )
        elif action == "delete":
            trade = self._selected_trade
            self.app.push_screen(
                ConfirmScreen(
                    f"Delete trade on {trade.date.strftime('%Y-%m-%d')} "
                    f"({trade.type.value.upper()} {trade.quantity} @ {trade.price:,.4f})?"
                ),
                lambda confirmed: self._delete_trade(trade.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete_trade(self, trade_id: int) -> None:
        try:
            api_service.delete_trade(trade_id)
        except Exception as exc:
            log.error(f"Failed to delete trade {trade_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    def _on_trade_saved(self, result: TradeRead | None) -> None:
        if result is not None:
            self._fetch_data()

    # ──────────────────────────────────────────────────────────────────
    # Transaction button handlers
    # ──────────────────────────────────────────────────────────────────

    @on(Button.Pressed, "#pe-add-transaction-btn")
    def on_add_transaction(self) -> None:
        self.app.push_screen(
            TransactionEdit(self._position.position_id, self._position.account_id),
            self._on_transaction_saved,
        )

    def _on_transaction_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(
                TransactionEdit(
                    self._position.position_id,
                    self._position.account_id,
                    self._selected_transaction,
                ),
                self._on_transaction_saved,
            )
        elif action == "delete":
            tx = self._selected_transaction
            self.app.push_screen(
                ConfirmScreen(
                    f"Delete {tx.type.value.upper()} transaction on "
                    f"{tx.date.strftime('%Y-%m-%d %H:%M')} ({tx.amount:,.2f})?"
                ),
                lambda confirmed: self._delete_transaction(tx.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete_transaction(self, transaction_id: int) -> None:
        try:
            api_service.delete_transaction(transaction_id)
        except Exception as exc:
            log.error(f"Failed to delete transaction {transaction_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    def _on_transaction_saved(self, result: TransactionRead | None) -> None:
        if result is not None:
            self._fetch_data()
