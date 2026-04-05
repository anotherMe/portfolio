import logging
from pathlib import Path
from typing import Iterable
log = logging.getLogger(__name__)

import requests
from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import Footer, Header, TabPane, TabbedContent, Static, Button
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.logging import TextualHandler
from textual import work

from api_service import API_URL, get_accounts, backup_database, load_ohlcv_from_json_file
from widgets.file_picker import FilePickerModal
from widgets.instruments_tab import InstrumentsTab
from widgets.positions_tab import PositionsTab
from widgets.trades_tab import TradesTab
from widgets.transactions_tab import TransactionsTab
from widgets.accounts_tab import AccountsTab
from widgets.prices_tab import PricesTab

logging.basicConfig(
    level="DEBUG",
    handlers=[TextualHandler()],
)

class BackendOfflineScreen(Screen):
    """Shown when the backend API cannot be reached at startup."""

    CSS = """
    BackendOfflineScreen {
        align: center middle;
    }
    #offline-container {
        width: 64;
        height: auto;
        border: round red;
        padding: 2 4;
    }
    #offline-title {
        text-align: center;
        color: red;
        text-style: bold;
        margin-bottom: 1;
    }
    #offline-message {
        text-align: center;
        margin-bottom: 2;
    }
    #offline-buttons {
        align: center middle;
        height: auto;
    }
    #offline-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="offline-container"):
            yield Static("Backend Unavailable", id="offline-title")
            yield Static(
                f"Cannot connect to the backend at [bold]{API_URL}[/bold].\n"
                "Please start the API server and press Retry.",
                id="offline-message",
            )
            with Horizontal(id="offline-buttons"):
                yield Button("Retry", id="retry-btn", variant="primary")
                yield Button("Quit", id="quit-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit-btn":
            self.app.exit()
        elif event.button.id == "retry-btn":
            self.query_one("#retry-btn", Button).disabled = True
            self._retry()

    @work(thread=True)
    def _retry(self) -> None:
        try:
            accounts = get_accounts()
            self.app.call_from_thread(self.dismiss, accounts)
        except requests.exceptions.ConnectionError:
            self.app.call_from_thread(self._on_retry_failed)

    def _on_retry_failed(self) -> None:
        self.query_one("#retry-btn", Button).disabled = False


class StatusBar(Static):
    """A status bar showing app-wide state (current account, etc.)"""

class MyPortfolio(App):
    """Portfolio management Textual app."""

    CSS = """
    #status-bar {
        height: 1;
        background: blue;
        color: #a8d8ff;
        padding: 0 2;
        text-align: right;
    }
    """

    BINDINGS = [
        Binding("a", "cycle_account", "Change Account"),
    ]

    _accounts: list = []
    _account_idx: int = 0

    # Override command palette
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Toggle dark mode", "Toggle dark mode", self._toggle_dark)
        yield SystemCommand("Backup database", "Create a timestamped backup of the database", self._backup_database)
        yield SystemCommand("Load OHLCV from JSON file", "Import Yahoo Finance JSON file into OHLCV table", self._open_ohlcv_file_picker)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        with Vertical():
            with TabbedContent(initial="positions"):
                with TabPane("Positions", id="positions"):
                    yield PositionsTab()
                with TabPane("Instruments", id="instruments"):
                    yield InstrumentsTab()
                with TabPane("Transactions", id="transactions"):
                    yield TransactionsTab()
                with TabPane("Trades", id="trades"):
                    yield TradesTab()
                with TabPane("Accounts", id="accounts"):
                    yield AccountsTab()
                with TabPane("Prices", id="prices"):
                    yield PricesTab()
        yield StatusBar("  📂  Account: All Accounts", id="status-bar")

    def on_mount(self) -> None:
        """Load accounts on startup."""
        log.info("App initialized")
        self._load_accounts()

    @work(thread=True)
    def _load_accounts(self) -> None:
        """Fetch accounts from the backend in a worker thread."""
        try:
            accounts = get_accounts()
            self.app.call_from_thread(self._set_accounts, accounts)
        except requests.exceptions.ConnectionError:
            self.app.call_from_thread(self._on_backend_unavailable)

    def _set_accounts(self, accounts) -> None:
        self._accounts = [("All Accounts", None)] + [(acc.name, str(acc.id)) for acc in accounts]
        self._account_idx = 0
        self._update_status()

    def _on_backend_unavailable(self) -> None:
        self.push_screen(BackendOfflineScreen(), self._on_backend_reconnected)

    def _on_backend_reconnected(self, accounts) -> None:
        self._set_accounts(accounts)
        self._refresh_all_tabs()

    def _refresh_all_tabs(self) -> None:
        _, account_id = self._accounts[self._account_idx]
        for tab_class in ("InstrumentsTab", "AccountsTab", "PricesTab"):
            try:
                self.query_one(tab_class).reload()
            except Exception:
                pass
        try:
            self.query_one("PositionsTab").reload(account_id)
        except Exception:
            pass
        try:
            self.query_one("TradesTab").reload(account_id)
        except Exception:
            pass
        try:
            self.query_one("TransactionsTab").reload(account_id)
        except Exception:
            pass

    def _update_status(self) -> None:
        """Update the status bar with the currently selected account."""
        name, _ = self._accounts[self._account_idx]
        self.query_one("#status-bar", StatusBar).update(
            f"  📂  Account: [bold italic]{name}[/bold italic]"
        )

    def _backup_database(self) -> None:
        """Trigger a database backup via the API."""
        try:
            path = backup_database()
            self.notify(f"Backup created: {path}", title="Backup", severity="information")
        except Exception as exc:
            self.notify(str(exc), title="Backup failed", severity="error")

    def _open_ohlcv_file_picker(self) -> None:
        """Open the file picker modal to select a Yahoo Finance JSON file."""
        self.push_screen(
            FilePickerModal(
                title="Select Yahoo Finance JSON file",
                start_path=Path.home(),
                extensions=[".json"],
            ),
            self._on_ohlcv_file_selected,
        )

    def _on_ohlcv_file_selected(self, path: Path | None) -> None:
        if path is None:
            return
        self._load_ohlcv_from_file(str(path))

    @work(thread=True)
    def _load_ohlcv_from_file(self, file_path: str) -> None:
        """Call the backend to load OHLCV data from the selected JSON file."""
        try:
            result = load_ohlcv_from_json_file(file_path)
            if result.get("success"):
                self.app.call_from_thread(
                    self.notify,
                    result["message"],
                    title="OHLCV Import",
                    severity="information",
                )
                try:
                    self.app.call_from_thread(self.query_one("PricesTab").get_instruments_with_prices)
                except Exception:
                    pass
            else:
                self.app.call_from_thread(
                    self.notify,
                    result["message"],
                    title="OHLCV Import failed",
                    severity="error",
                )
        except Exception as exc:
            self.app.call_from_thread(
                self.notify,
                str(exc),
                title="OHLCV Import failed",
                severity="error",
            )

    def _toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_cycle_account(self) -> None:
        """Cycle to the next account and refresh account-dependent tabs."""

        self._account_idx = (self._account_idx + 1) % len(self._accounts)
        _, account_id = self._accounts[self._account_idx]
        self._update_status()

        try:
            self.query_one("PositionsTab").reload(account_id)
        except Exception:
            pass
        try:
            self.query_one("TradesTab").reload(account_id)
        except Exception:
            pass
        try:
            self.query_one("TransactionsTab").reload(account_id)
        except Exception:
            pass


if __name__ == "__main__":
    app = MyPortfolio()
    app.run()