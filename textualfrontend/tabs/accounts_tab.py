from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable
from textual.containers import Vertical

from schemas.account import AccountRead
from api_service import get_accounts
import api_service
from edit.account_edit import AccountActionsModal, AccountEditModal
from widgets.confirm_screen import ConfirmScreen

import logging
log = logging.getLogger(__name__)


class AccountsTab(Vertical):
    """The Accounts tab content."""

    def compose(self) -> ComposeResult:
        yield DataTable(id="accounts_table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#accounts_table", DataTable)
        table.add_columns("ID", "Name", "Description")
        self._accounts: dict[str, AccountRead] = {}
        self._selected: AccountRead | None = None
        self._fetch_data()

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

    def _on_saved(self, result: AccountRead | None) -> None:
        if result is not None:
            self._fetch_data()
