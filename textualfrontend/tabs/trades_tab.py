
from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical, Horizontal
from api_service import get_trades


class TradeEdit(Vertical):
    """A custom widget representing the edit view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("No Trade selected", id="trade-edit-content")
        # A button to go back to the datatable
        yield Button("← Back to List", id="trade-back-button", variant="primary")

class TradeDetails(Horizontal):
    """A custom widget representing the details view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("Trade Details Here", id="trade-details-content")

class TradesList(Vertical):
    """Trades list (DataTable) on top half and the details view on the bottom half"""
    
    def compose(self) -> ComposeResult:
        table = DataTable(id="trades_table", cursor_type="row")
        table.styles.height = "2fr"
        yield table

        details = TradeDetails(id="trade_details")
        details.styles.height = "1fr"
        yield details

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
    
        table = self.query_one("#trades_table", DataTable)
        
        self.columns_to_show = ["date", "type", "quantity", "price", "description"]
        table.add_columns(*self.columns_to_show)

        trades = get_trades()
        if trades:
            self._populate_table(trades, table)

    @work(exclusive=True, thread=True)
    def refresh_table(self, account_id: str = None) -> None:
        """Clear and repopulate the table filtered by account_id."""
        table = self.query_one("#trades_table", DataTable)
        trades = get_trades(account_id)
        if trades:
            self._populate_table(trades, table)

    def _populate_table(self, trades, table):
        table.clear()
        for trade in trades:
            table.add_row(*trade.model_dump(include=set(self.columns_to_show)).values(), key=str(trade.id))

class TradesTab(Vertical):
    """The Trades tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="trades_switcher", initial="trades_list"):
            yield TradesList(id="trades_list")
            yield TradeEdit(id="trade_edit")

    @on(DataTable.RowSelected, "#trades_table")
    def on_trades_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        trade_id = row_key.value
        row_data = table.get_row(row_key)
        
        edit_label = self.query_one("#trade-edit-content", Static)
        edit_label.update(f"Editing / Viewing details for:\n\n**ID:** {trade_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#trades_switcher", ContentSwitcher)
        switcher.current = "trade_edit"

    @on(DataTable.RowHighlighted, "#trades_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted ) -> None:
        """Handle a row being highlighted (e.g., by pressing arrow keys)."""
        table = event.data_table
        row_key = event.row_key
        trade_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#trade-details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {trade_id}\n**Data:** {row_data}")

    @on(Button.Pressed, "#trade-back-button")
    def show_trade_list(self) -> None:
        """Triggered when the 'Back' button is clicked."""
        switcher = self.query_one("#trades_switcher", ContentSwitcher)
        switcher.current = "trades_list"
        self.query_one("#trades_list", TradesList).focus()
