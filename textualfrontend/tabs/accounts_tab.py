from textual.app import ComposeResult
from textual import on, work
from textual.binding import Binding
from textual.widgets import Button, DataTable
from textual.containers import Horizontal, Vertical

from schemas.account import AccountRead
from api_service import get_accounts
import api_service
from edit.account_edit import AccountActionsModal, AccountCreateModal, AccountEditModal
from widgets.confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


class AccountsTab(Vertical):
    """The Accounts tab content."""

    BINDINGS = [
        Binding("d", "delete_account", "Delete current account"),
    ]

    DEFAULT_CSS = """
    AccountsTab {
        height: 1fr;
    }
    AccountsTab #accounts_table {
        height: 1fr;
    }
    AccountsTab #accounts-toolbar {
        height: auto;
        align-horizontal: right;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield DataTable(id="accounts_table", cursor_type="row")
        with Horizontal(id="accounts-toolbar"):
            yield Button("+ Add Account", id="btn-add-account", variant="success")

    def on_mount(self) -> None:
        table = self.query_one("#accounts_table", DataTable)
        table.add_columns("ID", "Name", "Description")
        self._accounts: dict[str, AccountRead] = {}
        self._selected: AccountRead | None = None
        self._fetch_data()

    def _action_delete_account(self) -> None:
        # Get the actual highlighted row in the table
        table = self.query_one("#accounts_table", DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        self._selected = self._accounts.get(str(row_key.value))
        # Use the action handler to delete self._selected
        self._on_action("delete")

    # ── Data ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _fetch_data(self) -> None:
        try:
            accounts = get_accounts()
        except Exception as exc:
            log.error(f"Failed to load accounts: {exc}")
            accounts = []
        self.app.call_from_thread(self._populate, accounts)

    def _populate(self, accounts: list[AccountRead]) -> None:
        self._accounts = {str(a.id): a for a in accounts}
        self._selected = None
        table = self.query_one("#accounts_table", DataTable)
        table.clear()
        for a in accounts:
            table.add_row(
                str(a.id),
                a.name,
                a.description or "",
                key=str(a.id),
            )

    # ── Row selection ──────────────────────────────────────────────────

    @on(DataTable.RowSelected, "#accounts_table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        account = self._accounts.get(str(event.row_key.value)) if event.row_key else None
        if account is None:
            return
        self._selected = account
        self.app.push_screen(AccountActionsModal(account), self._on_action)

    # ── Action callbacks ───────────────────────────────────────────────

    def _on_action(self, action: str | None) -> None:
        if action == "edit":
            self.app.push_screen(
                AccountEditModal(self._selected),
                self._on_saved,
            )
        elif action == "delete":
            account = self._selected
            self.app.push_screen(
                ConfirmScreen(f"Delete account {account.name}?"),
                lambda confirmed: self._delete(account.id) if confirmed else None,
            )

    @work(thread=True)
    def _delete(self, account_id: int) -> None:
        try:
            api_service.delete_account(account_id)
        except Exception as exc:
            log.error(f"Failed to delete account {account_id}: {exc}")
        self.app.call_from_thread(self._fetch_data)

    @on(Button.Pressed, "#btn-add-account")
    def on_add_account(self) -> None:
        self.app.push_screen(AccountCreateModal(), self._on_saved)

    def _on_saved(self, result: AccountRead | None) -> None:
        if result is not None:
            self._fetch_data()
