
from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable, ContentSwitcher, Button, Static, Input, Select
from textual.containers import Right, Vertical, Horizontal
from textual.binding import Binding
from textual.screen import ModalScreen
from api_service import get_positions
from rich.text import Text

import logging
log = logging.getLogger(__name__)


class Filter():
    """A simple class to hold filter values for positions."""
    def __init__(self, instrument_name: str = "", isin: str = "", ticker: str = ""):
        self.instrument_name = instrument_name
        self.isin = isin
        self.ticker = ticker
        self.position_status = "all"  # "open", "closed", or "all"

class PositionFilter(ModalScreen[Filter]):
    """A collapsible widget for filtering positions."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Filter Positions", id="filter_title")
            yield Select(   
                (("Open", "open"), ("Closed", "closed"), ("All", "all")),
                value="all",
                id="filter_position_status"
            )
            yield Input(placeholder="Filter by Instrument Name", id="filter_instrument_name")
            yield Input(placeholder="Filter by Ticker", id="filter_ticker")
            yield Input(placeholder="Filter by ISIN", id="filter_isin")
            with Right():
                yield Button("Clear filters", id="clear_filters", variant="primary")
                yield Button("Apply filters", id="apply_filters", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the filter modal."""

        filter = Filter()
        if event.button.id == "apply_filters":
            filter.instrument_name = self.query_one("#filter_instrument_name", Input).value
            filter.isin = self.query_one("#filter_isin", Input).value
            filter.ticker = self.query_one("#filter_ticker", Input).value
            filter.position_status = self.query_one("#filter_position_status", Select).value
        
        self.dismiss(filter)  # Dismiss with empty filter to indicate clearing


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

        # with Collapsible(title="Filter", id="filters_collapsible", collapsed=True):
        #     filter = PositionFilter(id="position_filter")
        #     yield filter    

        table = DataTable(id="positions_table", cursor_type="row")
        table.styles.height = "2fr"
        yield table

        details = PositionDetails(id="position_details")
        details.styles.height = "1fr"
        yield details

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        
        table = self.query_one("#positions_table", DataTable)

        self.columns_to_show = [
            "instrument_name", "instrument_isin", "instrument_ticker", 
            "opening_date", "total_invested", "latest_price", 
            "latest_price_date", "remaining_quantity", "pnl", 
            "pnl_percent", "position_closed", "closing_date",
        ]
        table.add_columns(*self.columns_to_show)

        positions = get_positions()
        if positions:
            self._populate_table(positions, table)

    @work(exclusive=True, thread=True)
    def refresh_table(self, account_id: int = None, filter: Filter = None) -> None:
        """Clear and repopulate the table filtered by account_id."""

        table = self.query_one("#positions_table", DataTable)
        positions = get_positions(account_id=account_id, include_open=(filter.position_status in ["open", "all"]), include_closed=(filter.position_status in ["closed", "all"]))
        table.clear()
        if positions:
            self._populate_table(positions, table)


    def _populate_table(self, positions, table):
        
        for position in positions:
            
            row_data = position.model_dump(include=set(self.columns_to_show))
            
            # Convert pnl to formatted Rich Text (green/red + percentage)
            pnl_percent_value = row_data["pnl_percent"]
            pnl_percent_str = f"{pnl_percent_value:.1%}"  # e.g. "17.0%" or "-3.2%"
            pnl_color = "green" if pnl_percent_value >= 0 else "red"
            row_data["pnl_percent"] = Text(pnl_percent_str, style=pnl_color)
            
            table.add_row(*row_data.values(), key=str(position.position_id))

class PositionsTab(Vertical):
    """The Positions tab content."""

    BINDINGS = [
        Binding("f", "filter", "Show Filters"),
    ]

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

    def action_filter(self) -> None:
        """Show the filter modal"""
        # log.info("Toggling filter collapsible")
        # collapsible = self.query_one("#filters_collapsible", Collapsible)
        # collapsible.collapsed = not collapsible.collapsed

        def check_quit(filter: Filter) -> None:
            """Called when QuitScreen is dismissed."""
            if filter:
                log.info(f"Filters applied: Instrument Name: {filter.instrument_name}, ISIN: {filter.isin}, Ticker: {filter.ticker}, Position Status: {filter.position_status}")
                # TODO: Apply filters to the PositionsList based on the values entered in the PositionFilter screen
                pass

        self.app.push_screen(PositionFilter(), check_quit)
