from textual.app import ComposeResult
from textual import on
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical, Horizontal
from api_service import get_instruments

class InstrumentEdit(Vertical):
    """A custom widget representing the edit view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("Instrument editing Here", id="edit-content")
        # A button to go back to the datatable
        yield Button("← Back to List", id="back-button", variant="primary")

class InstrumentDetails(Horizontal):
    """A custom widget representing the details view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("Instrument Details Here", id="details-content")

class InstrumentList(Vertical):
    """Instruments list (DataTable) on top half and the details view on the bottom half"""
    
    def compose(self) -> ComposeResult:
        yield DataTable(id="instruments_table", cursor_type="row")
        yield InstrumentDetails(id="instrument_details")    

class InstrumentsTab(Vertical):
    """The Instruments tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="instruments_switcher", initial="instruments_list"):
            yield InstrumentList(id="instruments_list")
            yield InstrumentEdit(id="instrument_edit")

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
        
        edit_label = self.query_one("#edit-content", Static)
        edit_label.update(f"Editing / Viewing details for:\n\n**ID:** {instrument_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#instruments_switcher", ContentSwitcher)
        switcher.current = "instrument_edit"

    @on(DataTable.RowHighlighted, "#instruments_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted ) -> None:
        """Handle a row being highlighted (e.g., by pressing arrow keys)."""
        table = event.data_table
        row_key = event.row_key
        instrument_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {instrument_id}\n**Data:** {row_data}")

    @on(Button.Pressed, "#back-button")
    def show_instrument_list(self) -> None:
        """Triggered when the 'Back' button is clicked."""
        switcher = self.query_one("#instruments_switcher", ContentSwitcher)
        switcher.current = "instruments_list"
        self.query_one("#instruments_list", InstrumentList).focus()
