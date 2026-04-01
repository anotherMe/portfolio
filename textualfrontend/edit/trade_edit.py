from datetime import datetime, timezone

from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static
from textual.containers import Horizontal, Vertical

from enums import TradeType
from schemas.trade import TradeCreate, TradeRead, TradeUpdate
import api_service

import logging
log = logging.getLogger(__name__)


class TradeEdit(ModalScreen):
    """Modal form for creating or editing a Trade."""

    DEFAULT_CSS = """
    TradeEdit {
        align: center middle;
    }
    TradeEdit > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    TradeEdit .te-title {
        text-style: bold;
        padding-bottom: 1;
    }
    TradeEdit Label {
        padding: 0 0 0 0;
        color: $text-muted;
    }
    TradeEdit Input {
        margin-bottom: 1;
    }
    TradeEdit Select {
        margin-bottom: 1;
    }
    TradeEdit #te-error {
        color: $error;
        height: auto;
        margin-bottom: 1;
        display: none;
    }
    TradeEdit #te-buttons {
        height: auto;
        margin-top: 1;
    }
    TradeEdit #te-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, position_id: int | None = None, trade: TradeRead | None = None):
        super().__init__()
        self._position_id = position_id
        self._trade = trade

    def compose(self) -> ComposeResult:
        title = "Edit Trade" if self._trade else "Add Trade"
        with Vertical():
            yield Static(title, classes="te-title")
            if self._position_id is None and self._trade is None:
                yield Label("Position")
                yield Select([], id="te-position", prompt="Select a position…")
            yield Label("Date & Time (YYYY-MM-DD HH:MM)")
            yield Input(placeholder="YYYY-MM-DD HH:MM", id="te-date")
            yield Label("Type")
            yield Select(
                [(TradeType.BUY.value.capitalize(), TradeType.BUY.value),
                 (TradeType.SELL.value.capitalize(), TradeType.SELL.value)],
                id="te-type",
            )
            yield Label("Quantity")
            yield Input(placeholder="e.g. 10", id="te-quantity")
            yield Label("Price")
            yield Input(placeholder="e.g. 123.45", id="te-price")
            yield Label("Description (optional)")
            yield Input(placeholder="", id="te-description")
            yield Static("", id="te-error")
            with Horizontal(id="te-buttons"):
                yield Button("Save", id="te-save-btn", variant="success")
                yield Button("Cancel", id="te-cancel-btn")

    def on_mount(self) -> None:
        if self._trade:
            self.query_one("#te-date", Input).value = self._trade.date.strftime("%Y-%m-%d %H:%M")
            self.query_one("#te-type", Select).value = self._trade.type.value
            self.query_one("#te-quantity", Input).value = str(self._trade.quantity)
            self.query_one("#te-price", Input).value = str(self._trade.price)
            self.query_one("#te-description", Input).value = self._trade.description or ""
        else:
            self.query_one("#te-date", Input).value = datetime.now().strftime("%Y-%m-%d %H:%M")
        if self._position_id is None and self._trade is None:
            self._load_positions()

    @work(thread=True)
    def _load_positions(self) -> None:
        try:
            positions = api_service.get_positions(include_open=True, include_closed=False)
            options = [(f"{p.instrument_name} ({p.instrument_ticker})", str(p.position_id)) for p in positions]
        except Exception as exc:
            log.error(f"Failed to load positions: {exc}")
            options = []
        self.app.call_from_thread(
            lambda: self.query_one("#te-position", Select).set_options(options)
        )

    @on(Button.Pressed, "#te-cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#te-save-btn")
    def on_save(self) -> None:
        error = self._validate()
        if error:
            err_label = self.query_one("#te-error", Static)
            err_label.update(error)
            err_label.display = True
            return
        self.query_one("#te-save-btn", Button).disabled = True
        self._submit()

    def _validate(self) -> str | None:
        date_str = self.query_one("#te-date", Input).value.strip()
        qty_str = self.query_one("#te-quantity", Input).value.strip()
        price_str = self.query_one("#te-price", Input).value.strip()

        try:
            datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date/time. Use YYYY-MM-DD HH:MM format."

        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            return "Quantity must be a positive integer."

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            return "Price must be a positive number."

        if self.query_one("#te-type", Select).value is Select.BLANK:
            return "Please select a trade type."

        if self._position_id is None and self._trade is None:
            if self.query_one("#te-position", Select).value is Select.BLANK:
                return "Please select a position."

        return None

    @work(thread=True)
    def _submit(self) -> None:
        date_str = self.query_one("#te-date", Input).value.strip()
        type_val = self.query_one("#te-type", Select).value
        qty = int(self.query_one("#te-quantity", Input).value.strip())
        price = float(self.query_one("#te-price", Input).value.strip())
        desc = self.query_one("#te-description", Input).value.strip() or None

        trade_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

        position_id = self._position_id
        if position_id is None and self._trade is None:
            position_id = int(self.query_one("#te-position", Select).value)

        try:
            if self._trade:
                data = TradeUpdate(
                    date=trade_date,
                    type=TradeType(type_val),
                    quantity=qty,
                    price=price,
                    description=desc,
                )
                result = api_service.update_trade(self._trade.id, data)
            else:
                data = TradeCreate(
                    position_id=position_id,
                    date=trade_date,
                    type=TradeType(type_val),
                    quantity=qty,
                    price=price,
                    description=desc,
                )
                result = api_service.create_trade(data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to save trade: {exc}")
            self.app.call_from_thread(self._show_error, str(exc))

    def _show_error(self, message: str) -> None:
        err_label = self.query_one("#te-error", Static)
        err_label.update(message)
        err_label.display = True
        self.query_one("#te-save-btn", Button).disabled = False
