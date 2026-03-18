from textual.app import ComposeResult
from textual import on
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical, Horizontal
from api_service import get_positions

class PositionEdit(Vertical):
    """A custom widget representing the position detail view."""

    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("No Position selected", id="position-edit-content")
        # A button to go back to the datatable
        yield Button("← Back to List", id="position-back-button", variant="primary")

class PositionDetails(Horizontal):
    """A custom widget representing the position details view."""
    
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("Position Details Here", id="position-details-content")

class PositionsList(Vertical):
    """Positions list (DataTable) on top half and the details view on the bottom half"""
    
    def compose(self) -> ComposeResult:
        table = DataTable(id="positions_table", cursor_type="row")
        table.styles.height = "2fr"
        yield table

        details = PositionDetails(id="position_details")
        details.styles.height = "1fr"
        yield details

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        table = self.query_one("#positions_table", DataTable)
        positions = get_positions()

        if positions:
            columns_to_show = {
                "instrument_name", "instrument_isin", "instrument_ticker", 
                "opening_date", "total_invested", "latest_price", 
                "latest_price_date", "transactions_amount", "closing_date", 
                "remaining_quantity", "remaining_cost_basis", "realized_pnl", 
                "unrealized_pnl", "realized_pnl_percent", "unrealized_pnl_percent", 
                "pnl", "pnl_percent", "position_closed"
            }
            table.add_columns(*positions[0].model_dump(include=columns_to_show).keys())
            for position in positions:
                table.add_row(*position.model_dump(include=columns_to_show).values(), key=str(position.position_id))    

class PositionsTab(Vertical):
    """The Positions tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="positions_switcher", initial="positions_list"):
            yield PositionsList(id="positions_list")
            yield PositionEdit(id="position_edit")

    @on(DataTable.RowSelected, "#positions_table")
    def on_positions_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        position_id = row_key.value
        row_data = table.get_row(row_key)
        
        edit_label = self.query_one("#position-edit-content", Static)
        edit_label.update(f"Editing / Viewing details for:\n\n**ID:** {position_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#positions_switcher", ContentSwitcher)
        switcher.current = "position_edit"

    @on(DataTable.RowHighlighted, "#positions_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted ) -> None:
        """Handle a row being highlighted (e.g., by pressing arrow keys)."""
        table = event.data_table
        row_key = event.row_key
        position_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#position-details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {position_id}\n**Data:** {row_data}")

    @on(Button.Pressed, "#position-back-button")
    def show_position_list(self) -> None:
        """Triggered when the 'Back' button in positions tab is clicked."""
        switcher = self.query_one("#positions_switcher", ContentSwitcher)
        switcher.current = "positions_list"
        self.query_one("#positions_list", PositionsList).focus()
