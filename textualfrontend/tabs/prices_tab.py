
import logging
import asyncio
import time
log = logging.getLogger(__name__)

from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable, Button, Static, ProgressBar, Input
from textual.containers import Vertical, Right
from textual.binding import Binding
from textual.message import Message

from api_service import get_instruments_with_last_price, load_prices_for_instrument


class InstrumentPriceUpdateProgress(Message):
    def __init__(self, progress: int, instrument: str):
        super().__init__()
        self.progress = progress
        self.instrument = instrument

class InstrumentPricesUpdateComplete(Message):
    def __init__(self, message: str = "Prices loading completed successfully."):
        super().__init__()
        self.status_message = message

class InstrumentPricesUpdateError(Message):
    def __init__(self, message: str):
        super().__init__()
        self.status_message = message

class InstrumentPricesUpdateStopped(Message):
    def __init__(self, message: str = "Prices loading stopped by user."):
        super().__init__()
        self.status_message = message


class PricesTab(Vertical):
    """The Prices tab content."""

    DEFAULT_CSS = """
    PricesTab Right {
        margin-top: 1;
    }
    #start_loading {
        margin-right: 1;
    }
    """

    BINDINGS = [
        Binding("x", "stop_loading", "Stop loading prices"),
    ]

    def action_stop_loading(self) -> None:
        """Stop the price loading process."""
        log.info("Stopping price loading")
        if hasattr(self, "worker") and self.worker:
            self.worker.cancel()
            self.prices_loading = False
            self.query_one("#start_loading", Button).disabled = False
            self.update_status("Loading stopped by user.")

    def update_progress(self, progress: int) -> None:
        self.query_one("#progress_bar", ProgressBar).update(progress=progress)

    def update_current_instrument(self, name: str) -> None:
        self.query_one("#current_instrument", Static).update(f"Current: {name}")

    def update_status(self, msg: str) -> None:
        self.query_one("#status_message", Static).update(f"Status: {msg}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instruments = []
        self.prices_loading = False
        self.delay = 1  # seconds

    def compose(self) -> ComposeResult:
        with Vertical():
            table = DataTable(id="instruments_table", cursor_type="row")
            table.styles.height = "1fr"
            yield table
            with Right():
                yield Button("Start Price Loading", id="start_loading", variant="primary")
            yield ProgressBar(id="progress_bar", total=0)
            yield Static("Status: Ready", id="status_message")

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        
        log.info("Mounting PricesTab and loading instruments")
        self.get_instruments_with_prices()    

    @on(Button.Pressed, "#start_loading")
    def start_loading(self) -> None:
        """Start the price loading process."""
        
        if self.prices_loading:
            self.query_one("#status_message", Static).update("Status: Already loading")
            return

        self.prices_loading = True
        self.query_one("#start_loading", Button).disabled = True
        self.query_one("#status_message", Static).update("Status: Loading")
        self.current_index = 0
        self.query_one("#progress_bar", ProgressBar).update(total=len(self.instruments), progress=0)
        self.worker = self.load_all()

    def refresh_table(self, instruments) -> None:
        """Refresh the instruments table."""

        table = self.query_one("#instruments_table", DataTable)
        table.clear()
        if instruments:
            columns_to_show = {"name", "ticker", "last_price_date"}
            table.add_columns(*columns_to_show)
            for instrument in self.instruments:
                row_data = [
                    instrument.name,
                    instrument.ticker,
                    str(instrument.last_price_date) if instrument.last_price_date else "Never"
                ]
                table.add_row(*row_data, key=str(instrument.id))

    @work(exclusive=True, thread=True)
    def get_instruments_with_prices(self) -> None:
        """Refresh the instruments table."""

        self.instruments = get_instruments_with_last_price()
        self.app.call_from_thread(self.refresh_table, self.instruments)

    @work(exclusive=True, thread=True)
    def load_all(self) -> None:
        """Load prices for the next instrument."""

        try:
            while self.current_index < len(self.instruments):

                instrument = self.instruments[self.current_index]

                try:
                    result = load_prices_for_instrument(instrument.id)
                    self.app.call_from_thread(self.update_status, f"Loading {instrument.ticker}")
                    self.app.call_from_thread(self.update_current_instrument, instrument.ticker)
                    self.app.call_from_thread(self.update_progress, self.current_index + 1)
                except Exception as e:
                    log.error(f"Error loading prices for {instrument.ticker}: {str(e)}")
                    self.app.call_from_thread(self.update_status, f"Error {instrument.ticker}: {str(e)}")

                time.sleep(self.delay)  # don't push too much on Yahoo Finance API
                self.current_index += 1

            self.post_message(InstrumentPricesUpdateComplete())

        except asyncio.CancelledError:
            self.post_message(InstrumentPricesUpdateError("Loading cancelled by user."))
            raise

    @on(InstrumentPricesUpdateComplete)
    @on(InstrumentPricesUpdateError)
    @on(InstrumentPricesUpdateStopped)
    def handle_prices_update_complete(self, message) -> None:
        self.prices_loading = False
        self.query_one("#start_loading", Button).disabled = False
        self.query_one("#progress_bar", ProgressBar).update(total=len(self.instruments), progress=0)
        self.update_current_instrument("None")
        self.get_instruments_with_prices()
        self.update_status(message.status_message)
