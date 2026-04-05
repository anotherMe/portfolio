from textual.app import ComposeResult
from textual import on, work
from textual.widgets import Button, DataTable
from textual.containers import Horizontal, Vertical

from schemas.instrument import InstrumentRead
from api_service import get_instruments
import api_service
from .instrument_edit import InstrumentActionsModal, InstrumentCreateModal, InstrumentEditModal
from .confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


class InstrumentsTab(Vertical):
    """The Instruments tab content."""

    DEFAULT_CSS = """
    InstrumentsTab {
        height: 1fr;
    }
    InstrumentsTab #instruments_table {
        height: 1fr;
    }
    InstrumentsTab #instruments-toolbar {
        height: auto;
        align-horizontal: right;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield DataTable(id="instruments_table", cursor_type="row")
        with Horizontal(id="instruments-toolbar"):
            yield Button("+ Add Instrument", id="btn-add-instrument", variant="success")

    def on_mount(self) -> None:
        table = self.query_one("#instruments_table", DataTable)
        table.add_columns("Name", "Ticker", "ISIN", "Currency", "Category")
        self._instruments: dict[str, InstrumentRead] = {}
        self._selected: InstrumentRead | None = None
        self._fetch_data()

    # ── Data ──────────────────────────────────────────────────────────

    def reload(self) -> None:
        self._fetch_data()

    @work(thread=True)
    def _fetch_data(self) -> None:
        try:
            instruments = get_instruments()
        except Exception as exc:
            log.error(f"Failed to load instruments: {exc}")
            instruments = []
        self.app.call_from_thread(self._populate, instruments)

    def _populate(self, instruments: list[InstrumentRead]) -> None:
        self._instruments = {str(i.id): i for i in instruments}
        self._selected = None
        table = self.query_one("#instruments_table", DataTable)
        table.clear()
        for i in instruments:
            table.add_row(
                i.name,
                i.ticker or "",
                i.isin or "",
                i.currency,
                i.category or "",
                key=str(i.id),
            )

    # ── Row selection ──────────────────────────────────────────────────

    @on(DataTable.RowSelected, "#instruments_table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        instrument = self._instruments.get(str(event.row_key.value)) if event.row_key else None
        if instrument is None:
            return
        self._selected = instrument
        self.app.push_screen(InstrumentActionsModal(instrument), self._on_action)

    # ── Action callbacks ───────────────────────────────────────────────

    def _on_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(InstrumentEditModal(self._selected), self._on_saved)
        elif action == "delete":
            instrument = self._selected
            self.app.push_screen(
                ConfirmScreen(f"Delete instrument {instrument.name}?"),
                lambda confirmed: self._delete(instrument.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete(self, instrument_id: int) -> None:
        try:
            api_service.delete_instrument(instrument_id)
        except Exception as exc:
            log.error(f"Failed to delete instrument {instrument_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    @on(Button.Pressed, "#btn-add-instrument")
    def on_add_instrument(self) -> None:
        self.app.push_screen(InstrumentCreateModal(), self._on_saved)

    def _on_saved(self, result: InstrumentRead | None) -> None:
        if result is not None:
            self._fetch_data()
