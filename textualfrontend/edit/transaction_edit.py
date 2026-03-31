from datetime import datetime, timezone

from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static
from textual.containers import Horizontal, Vertical

from enums import TransactionType
from schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
import api_service

import logging
log = logging.getLogger(__name__)


class TransactionEdit(ModalScreen):
    """Modal form for creating or editing a Transaction."""

    DEFAULT_CSS = """
    TransactionEdit {
        align: center middle;
    }
    TransactionEdit > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    TransactionEdit .txe-title {
        text-style: bold;
        padding-bottom: 1;
    }
    TransactionEdit Label {
        padding: 0 0 0 0;
        color: $text-muted;
    }
    TransactionEdit Input {
        margin-bottom: 1;
    }
    TransactionEdit Select {
        margin-bottom: 1;
    }
    TransactionEdit #txe-error {
        color: $error;
        height: auto;
        margin-bottom: 1;
        display: none;
    }
    TransactionEdit #txe-buttons {
        height: auto;
        margin-top: 1;
    }
    TransactionEdit #txe-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, position_id: int, account_id: int, transaction: TransactionRead | None = None):
        super().__init__()
        self._position_id = position_id
        self._account_id = account_id
        self._transaction = transaction

    def compose(self) -> ComposeResult:
        title = "Edit Transaction" if self._transaction else "Add Transaction"
        with Vertical():
            yield Static(title, classes="txe-title")
            yield Label("Date & Time (YYYY-MM-DD HH:MM)")
            yield Input(placeholder="YYYY-MM-DD HH:MM", id="txe-date")
            yield Label("Type")
            yield Select(
                [(t.value.upper(), t.value) for t in TransactionType],
                id="txe-type",
            )
            yield Label("Amount")
            yield Input(placeholder="e.g. 12.50", id="txe-amount")
            yield Label("Description (optional)")
            yield Input(placeholder="", id="txe-description")
            yield Static("", id="txe-error")
            with Horizontal(id="txe-buttons"):
                yield Button("Save", id="txe-save-btn", variant="success")
                yield Button("Cancel", id="txe-cancel-btn")

    def on_mount(self) -> None:
        if self._transaction:
            self.query_one("#txe-date", Input).value = self._transaction.date.strftime("%Y-%m-%d %H:%M")
            self.query_one("#txe-type", Select).value = self._transaction.type.value
            self.query_one("#txe-amount", Input).value = str(self._transaction.amount)
            self.query_one("#txe-description", Input).value = self._transaction.description or ""
        else:
            self.query_one("#txe-date", Input).value = datetime.now().strftime("%Y-%m-%d %H:%M")

    @on(Button.Pressed, "#txe-cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#txe-save-btn")
    def on_save(self) -> None:
        error = self._validate()
        if error:
            err_label = self.query_one("#txe-error", Static)
            err_label.update(error)
            err_label.display = True
            return
        self.query_one("#txe-save-btn", Button).disabled = True
        self._submit()

    def _validate(self) -> str | None:
        date_str = self.query_one("#txe-date", Input).value.strip()
        amount_str = self.query_one("#txe-amount", Input).value.strip()

        try:
            datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date/time. Use YYYY-MM-DD HH:MM format."

        try:
            amount = float(amount_str)
            if amount == 0:
                raise ValueError
        except ValueError:
            return "Amount must be a non-zero number."

        if self.query_one("#txe-type", Select).value is Select.BLANK:
            return "Please select a transaction type."

        return None

    @work(thread=True)
    def _submit(self) -> None:
        date_str = self.query_one("#txe-date", Input).value.strip()
        type_val = self.query_one("#txe-type", Select).value
        amount = float(self.query_one("#txe-amount", Input).value.strip())
        desc = self.query_one("#txe-description", Input).value.strip() or None

        tx_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

        try:
            if self._transaction:
                data = TransactionUpdate(
                    date=tx_date,
                    type=TransactionType(type_val),
                    amount=amount,
                    description=desc,
                )
                result = api_service.update_transaction(self._transaction.id, data)
            else:
                data = TransactionCreate(
                    account_id=self._account_id,
                    position_id=self._position_id,
                    date=tx_date,
                    type=TransactionType(type_val),
                    amount=amount,
                    description=desc,
                )
                result = api_service.create_transaction(data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to save transaction: {exc}")
            self.app.call_from_thread(self._show_error, str(exc))

    def _show_error(self, message: str) -> None:
        err_label = self.query_one("#txe-error", Static)
        err_label.update(message)
        err_label.display = True
        self.query_one("#txe-save-btn", Button).disabled = False
