from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static
from textual.containers import Horizontal, Vertical

from schemas.instrument import InstrumentCreate, InstrumentRead, InstrumentUpdate
from enums import Currency, InstrumentCategory
import api_service

import logging
log = logging.getLogger(__name__)


class InstrumentActionsModal(ModalScreen):
    """Modal shown when an instrument row is selected."""

    BINDINGS = [("escape", "dismiss", "Cancel")]

    DEFAULT_CSS = """
    InstrumentActionsModal {
        align: center middle;
    }
    InstrumentActionsModal > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }
    InstrumentActionsModal #modal-info {
        padding-bottom: 1;
    }
    InstrumentActionsModal #modal-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    InstrumentActionsModal #modal-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, instrument: InstrumentRead, **kwargs):
        super().__init__(**kwargs)
        self._instrument = instrument

    def compose(self) -> ComposeResult:
        i = self._instrument
        with Vertical():
            yield Static(
                f"[bold]{i.name}[/bold]"
                + (f"  [{i.ticker}]" if i.ticker else "")
                + (f"  {i.isin}" if i.isin else "")
                + (f"  {i.currency}" if i.currency else ""),
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


class InstrumentEditModal(ModalScreen):
    """Modal form for editing an Instrument."""

    DEFAULT_CSS = """
    InstrumentEditModal {
        align: center middle;
    }
    InstrumentEditModal > Vertical {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    InstrumentEditModal Label {
        margin-top: 1;
    }
    InstrumentEditModal #form-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    InstrumentEditModal #form-buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, instrument: InstrumentRead, **kwargs):
        super().__init__(**kwargs)
        self._instrument = instrument

    def compose(self) -> ComposeResult:
        i = self._instrument
        with Vertical():
            yield Static(f"Edit Instrument: [bold]{i.name}[/bold]")
            yield Label("Name *")
            yield Input(value=i.name or "", id="field-name")
            yield Label("Ticker")
            yield Input(value=i.ticker or "", id="field-ticker")
            yield Label("ISIN")
            yield Input(value=i.isin or "", id="field-isin")
            yield Label("Currency *")
            yield Select(
                [(c.name, c.name) for c in Currency],
                id="field-currency",
            )
            yield Label("Category")
            yield Select(
                [(c.value, c.value) for c in InstrumentCategory],
                allow_blank=True,
                prompt="—",
                id="field-category",
            )
            yield Label("Description")
            yield Input(value=i.description or "", id="field-description")
            with Horizontal(id="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save", id="btn-save", variant="success")

    def on_mount(self) -> None:
        i = self._instrument
        if i.currency:
            self.query_one("#field-currency", Select).value = i.currency
        if i.category:
            self.query_one("#field-category", Select).value = i.category

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        self._do_save()

    @work(thread=True)
    def _do_save(self) -> None:
        currency_val = self.query_one("#field-currency", Select).value
        category_val = self.query_one("#field-category", Select).value
        data = InstrumentUpdate(
            name=self.query_one("#field-name", Input).value or None,
            ticker=self.query_one("#field-ticker", Input).value or None,
            isin=self.query_one("#field-isin", Input).value or None,
            currency=currency_val if isinstance(currency_val, str) else None,
            category=category_val if isinstance(category_val, str) else None,
            description=self.query_one("#field-description", Input).value or None,
        )
        try:
            result = api_service.update_instrument(self._instrument.id, data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to update instrument {self._instrument.id}: {exc}")
            self.app.call_from_thread(self.dismiss, None)


class InstrumentCreateModal(ModalScreen):
    """Modal form for creating a new Instrument."""

    DEFAULT_CSS = InstrumentEditModal.DEFAULT_CSS.replace("InstrumentEditModal", "InstrumentCreateModal") + """
    InstrumentCreateModal #field-error {
        color: $error;
        height: auto;
        margin-bottom: 1;
        display: none;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Add Instrument")
            yield Label("Name *")
            yield Input(placeholder="Instrument name", id="field-name")
            yield Label("Ticker")
            yield Input(placeholder="e.g. AAPL", id="field-ticker")
            yield Label("ISIN")
            yield Input(placeholder="e.g. US0378331005", id="field-isin")
            yield Label("Currency *")
            yield Select(
                [(c.name, c.name) for c in Currency],
                id="field-currency",
            )
            yield Label("Category")
            yield Select(
                [(c.value, c.value) for c in InstrumentCategory],
                allow_blank=True,
                prompt="—",
                id="field-category",
            )
            yield Label("Description")
            yield Input(placeholder="Optional description", id="field-description")
            yield Static("", id="field-error")
            with Horizontal(id="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save", id="btn-save", variant="success")

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        error = self._validate()
        if error:
            err = self.query_one("#field-error", Static)
            err.update(error)
            err.display = True
            return
        self._do_save()

    def _validate(self) -> str | None:
        if not self.query_one("#field-name", Input).value.strip():
            return "Name is required."
        if not isinstance(self.query_one("#field-currency", Select).value, str):
            return "Currency is required."
        return None

    @work(thread=True)
    def _do_save(self) -> None:
        currency_val = self.query_one("#field-currency", Select).value
        category_val = self.query_one("#field-category", Select).value
        data = InstrumentCreate(
            name=self.query_one("#field-name", Input).value.strip(),
            ticker=self.query_one("#field-ticker", Input).value or None,
            isin=self.query_one("#field-isin", Input).value or None,
            currency=currency_val if isinstance(currency_val, str) else "",
            category=category_val if isinstance(category_val, str) else None,
            description=self.query_one("#field-description", Input).value or None,
        )
        try:
            result = api_service.create_instrument(data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to create instrument: {exc}")
            self.app.call_from_thread(self.dismiss, None)
