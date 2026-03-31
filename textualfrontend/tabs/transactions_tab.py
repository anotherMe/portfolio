from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable
from textual.containers import Vertical

from schemas.transaction import TransactionRead
from api_service import get_transactions
import api_service
from edit.position_edit import TransactionActionsModal
from edit.transaction_edit import TransactionEdit
from widgets.confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


class TransactionsTab(Vertical):
    """The Transactions tab content."""

    def compose(self) -> ComposeResult:
        yield DataTable(id="transactions_table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#transactions_table", DataTable)
        table.add_columns("Date", "Type", "Amount", "Description")
        self._transactions: dict[str, TransactionRead] = {}
        self._selected: TransactionRead | None = None
        self._fetch_data()

    # ── Data ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _fetch_data(self) -> None:
        try:
            transactions = get_transactions()
        except Exception as exc:
            log.error(f"Failed to load transactions: {exc}")
            transactions = []
        self.app.call_from_thread(self._populate, transactions)

    def _populate(self, transactions: list[TransactionRead]) -> None:
        self._transactions = {str(t.id): t for t in transactions}
        self._selected = None
        table = self.query_one("#transactions_table", DataTable)
        table.clear()
        for t in transactions:
            table.add_row(
                t.date.strftime("%Y-%m-%d"),
                t.type.value.upper(),
                f"{t.amount:,.2f}",
                t.description or "",
                key=str(t.id),
            )

    # ── Row selection ──────────────────────────────────────────────────

    @on(DataTable.RowSelected, "#transactions_table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        tx = self._transactions.get(str(event.row_key.value)) if event.row_key else None
        if tx is None:
            return
        self._selected = tx
        self.app.push_screen(TransactionActionsModal(tx), self._on_action)

    # ── Action callbacks ───────────────────────────────────────────────

    def _on_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(
                TransactionEdit(self._selected.position_id, self._selected.account_id, self._selected),
                self._on_saved,
            )
        elif action == "delete":
            tx = self._selected
            self.app.push_screen(
                ConfirmScreen(
                    f"Delete {tx.type.value.upper()} transaction on "
                    f"{tx.date.strftime('%Y-%m-%d')} ({tx.amount:,.2f})?"
                ),
                lambda confirmed: self._delete(tx.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete(self, transaction_id: int) -> None:
        try:
            api_service.delete_transaction(transaction_id)
        except Exception as exc:
            log.error(f"Failed to delete transaction {transaction_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    def _on_saved(self, result: TransactionRead | None) -> None:
        if result is not None:
            self._fetch_data()
