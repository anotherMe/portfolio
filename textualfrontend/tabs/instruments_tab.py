from textual.app import ComposeResult
from textual import on
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical
from api_service import get_instruments

class InstrumentDetails(Vertical):
    """A custom widget representing the detail view."""
    def compose(self) -> ComposeResult:
        # A button to go back to the datatable
        yield Button("← Back to List", id="back-button", variant="primary")
        # Placeholder for our details
        yield Static("Instrument Details Here", id="details-content")


class InstrumentsTab(Vertical):
    """The Instruments tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="instruments_table", id="instruments_switcher"):
            table = DataTable(id="instruments_table", cursor_type="row")
            yield table
            yield InstrumentDetails(id="instrument_details")

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        table = self.query_one("#instruments_table", DataTable)
        instruments = get_instruments()

        if instruments:
            columns_to_show = {"name", "ticker", "category", "currency"}
            table.add_columns(*instruments[0].model_dump(include=columns_to_show).keys())
            for instrument in instruments:
                table.add_row(*instrument.model_dump(include=columns_to_show).values(), key=str(instrument.id))

    @on(DataTable.RowSelected, "#instruments_table")
    def on_instruments_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        instrument_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {instrument_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#instruments_switcher", ContentSwitcher)
        switcher.current = "instrument_details"

    @on(Button.Pressed, "#back-button")
    def show_instrument_list(self) -> None:
        """Triggered when the 'Back' button is clicked."""
        switcher = self.query_one("#instruments_switcher", ContentSwitcher)
        switcher.current = "instruments_table"
        self.query_one("#instruments_table", DataTable).focus()
