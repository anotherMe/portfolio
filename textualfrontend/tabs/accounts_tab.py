from textual.app import ComposeResult
from textual import on
from textual.widgets import DataTable, ContentSwitcher, Button, Static
from textual.containers import Vertical, Horizontal
from api_service import get_accounts

class AccountEdit(Vertical):
    """A custom widget representing the edit view."""
    def compose(self) -> ComposeResult:
        yield Static("No Account selected", id="account-edit-content")
        yield Button("← Back to List", id="account-back-button", variant="primary")

class AccountDetails(Horizontal):
    """A custom widget representing the details view."""
    def compose(self) -> ComposeResult:
        yield Static("Account Details Here", id="account-details-content")

class AccountsList(Vertical):
    """Accounts list (DataTable) on top half and the details view on the bottom half"""
    
    def compose(self) -> ComposeResult:
        table = DataTable(id="accounts_table", cursor_type="row")
        table.styles.height = "2fr"
        yield table

        details = AccountDetails(id="account_details")
        details.styles.height = "1fr"
        yield details

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""
        table = self.query_one("#accounts_table", DataTable)
        accounts = get_accounts()

        if accounts:
            columns_to_show = ["id", "name", "description"]
            table.add_columns(*columns_to_show)
            for acc in accounts:
                table.add_row(*acc.model_dump(include=set(columns_to_show)).values(), key=str(acc.id))

class AccountsTab(Vertical):
    """The Accounts tab content."""

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="accounts_switcher", initial="accounts_list"):
            yield AccountsList(id="accounts_list")
            yield AccountEdit(id="account_edit")

    @on(DataTable.RowSelected, "#accounts_table")
    def on_accounts_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row_key = event.row_key
        acc_id = row_key.value
        row_data = table.get_row(row_key)
        
        edit_label = self.query_one("#account-edit-content", Static)
        edit_label.update(f"Editing / Viewing details for:\n\n**ID:** {acc_id}\n**Data:** {row_data}")
        
        switcher = self.query_one("#accounts_switcher", ContentSwitcher)
        switcher.current = "account_edit"

    @on(DataTable.RowHighlighted, "#accounts_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted ) -> None:
        table = event.data_table
        row_key = event.row_key
        acc_id = row_key.value
        row_data = table.get_row(row_key)
        
        details_label = self.query_one("#account-details-content", Static)
        details_label.update(f"Editing / Viewing details for:\n\n**ID:** {acc_id}\n**Data:** {row_data}")

    @on(Button.Pressed, "#account-back-button")
    def show_account_list(self) -> None:
        switcher = self.query_one("#accounts_switcher", ContentSwitcher)
        switcher.current = "accounts_list"
        self.query_one("#accounts_list", AccountsList).focus()
