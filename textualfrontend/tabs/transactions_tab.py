from textual.app import ComposeResult
from textual import on
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical, Horizontal
from api_service import get_transactions

class TransactionEdit(Vertical):
    """A custom widget representing the edit view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("No Transaction selected", id="transaction-edit-content")
        # A button to go back to the datatable
        yield Button("← Back to List", id="transaction-back-button", variant="primary")

class TransactionDetails(Horizontal):
    """A custom widget representing the details view."""
    def compose(self) -> ComposeResult:
        # Placeholder for our details
        yield Static("Transaction Details Here", id="transaction-details-content")

class TransactionsList(Vertical):
    """Transactions list (DataTable) on top half and the details view on the bottom half"""
    
    def compose(self) -> ComposeResult:
        table = DataTable(id="transactions_table", cursor_type="row")
        table.styles.height = "2fr"
        yield table
        
        details = TransactionDetails(id="transaction_details")
        details.styles.height = "1fr"
        yield details

    async def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        table = self.query_one("#transactions_table", DataTable)
        transactions = get_transactions()

        if transactions:
            columns_to_show = ["date", "type", "amount", "description"]
            table.add_columns(*columns_to_show)
            for tx in transactions:
                table.add_row(*tx.model_dump(include=set(columns_to_show)).values(), key=str(tx.id))

    async def refresh_table(self, account_id: str = None) -> None:
        """Clear and repopulate the table filtered by account_id."""
        table = self.query_one("#transactions_table", DataTable)
        table.clear()
        transactions = get_transactions(account_id)
        for tx in transactions:
            columns_to_show = ["date", "type", "amount", "description"]
            table.add_row(*tx.model_dump(include=set(columns_to_show)).values(), key=str(tx.id))

class TransactionsTab(Vertical):
    """The Transactions tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="transactions_switcher", initial="transactions_list"):
            yield TransactionsList(id="transactions_list")
            yield TransactionEdit(id="transaction_edit")

    @on(DataTable.RowSelected, "#transactions_table")
    def on_transactions_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        tx_id = row_key.value
        row_data = table.get_row(row_key)
        
        edit_label = self.query_one("#transaction-edit-content", Static)
        edit_label.update(f"Editing / Viewing details for:\n\n**ID:** {tx_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#transactions_switcher", ContentSwitcher)
        switcher.current = "transaction_edit"

    @on(DataTable.RowHighlighted, "#transactions_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted ) -> None:
        """Handle a row being highlighted (e.g., by pressing arrow keys)."""
        table = event.data_table
        row_key = event.row_key
        tx_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#transaction-details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {tx_id}\n**Data:** {row_data}")

    @on(Button.Pressed, "#transaction-back-button")
    def show_transaction_list(self) -> None:
        """Triggered when the 'Back' button is clicked."""
        switcher = self.query_one("#transactions_switcher", ContentSwitcher)
        switcher.current = "transactions_list"
        self.query_one("#transactions_list", TransactionsList).focus()
