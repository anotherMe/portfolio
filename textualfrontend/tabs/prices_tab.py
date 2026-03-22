
import logging
import asyncio
log = logging.getLogger(__name__)

from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable, Button, Static, ProgressBar, Input
from textual.containers import Vertical, Right
from textual.binding import Binding
from textual.message import Message

from api_service import get_instruments_with_last_price, load_prices_for_instrument

# class InstrumentPriceUpdateProgress(Message):
#     def __init__(self, progress: int, instrument: str):
#         super().__init__()
#         self.progress = progress
#         self.instrument = instrument

class PricesTab(Vertical):
    """The Prices tab content."""

    # BINDINGS = [
    #     Binding("x", "stop_loading", "Stop loading prices"),
    # ]

    # def action_stop_loading(self) -> None:
    #     """Stop the price loading process."""
    #     log.info("Stopping price loading")
    #     if hasattr(self, 'worker') and self.worker:
    #         self.worker.cancel()

    def update_progress(self, progress: int) -> None:
        self.query_one("#progress_bar", ProgressBar).update(progress=progress)

    def update_current_instrument(self, name: str) -> None:
        self.query_one("#current_instrument", Static).update(f"Current: {name}")

    def update_status(self, msg: str) -> None:
        self.query_one("#status_message", Static).update(f"Status: {msg}")

    # def finish_completed(self) -> None:
    #     self.loading = False
    #     self.query_one("#start_loading", Button).disabled = False
    #     self.update_current_instrument("None")
    #     self.run_worker(self.refresh_table())
    #     self.update_status("Completed")

    # def finish_stopped(self) -> None:
    #     self.loading = False
    #     self.query_one("#start_loading", Button).disabled = False
    #     self.update_current_instrument("None")
    #     self.run_worker(self.refresh_table())
    #     self.update_status("Stopped")

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
            yield Static("Current: None", id="current_instrument")
            yield Static("Status: Ready", id="status_message")

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        
        log.info("Mounting PricesTab and loading instruments")
        self.get_instruments_with_prices()    

    @on(Button.Pressed, "#start_loading")
    async def start_loading(self) -> None:
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
    async def get_instruments_with_prices(self) -> None:
        """Refresh the instruments table."""

        self.instruments = get_instruments_with_last_price()
        self.app.call_from_thread(self.refresh_table, self.instruments)

    @work(exclusive=True, thread=True)
    async def load_all(self) -> None:
        """Load prices for the next instrument."""
        try:
            while self.current_index < len(self.instruments):
                instrument = self.instruments[self.current_index]
                log.info(f"Loading prices for {instrument.name} ({instrument.ticker})")
                self.app.call_from_thread(self.update_current_instrument, instrument.name)
                self.app.call_from_thread(self.update_progress, self.current_index + 1)

                try:
                    result = load_prices_for_instrument(instrument.id)
                    # self.post_message(InstrumentPriceUpdateProgress(self.current_index + 1, f"Processed {instrument.name}: {result['message']}"))
                    self.app.call_from_thread(self.update_status, f"Loaded {instrument.ticker}")
                except Exception as e:
                    self.app.call_from_thread(self.update_status, f"Error {instrument.ticker}: {str(e)}")

                self.current_index += 1

            # Completed
            self.app.call_from_thread(self.finish_completed)
        except asyncio.CancelledError:
            self.app.call_from_thread(self.finish_stopped)
            raise

