from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabPane, TabbedContent, Static
from textual.containers import Vertical
from textual.binding import Binding
from textual.events import Resize

from api_service import get_accounts

# Import custom widgets
from tabs.instruments_tab import InstrumentsTab
from tabs.positions_tab import PositionsTab
from tabs.trades_tab import TradesTab
from tabs.transactions_tab import TransactionsTab
from tabs.accounts_tab import AccountsTab


class StatusBar(Static):
    """A status bar showing app-wide state (current account, etc.)"""

class MyFancyApp(App):
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
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("a", "cycle_account", "Change Account"),
    ]

    _accounts: list = []
    _account_idx: int = 0

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
        yield StatusBar("  📂  Account: All Accounts", id="status-bar")

    def on_mount(self) -> None:
        """Load accounts on startup."""
        accounts = get_accounts()
        self._accounts = [("All Accounts", None)] + [(acc.name, str(acc.id)) for acc in accounts]
        self._account_idx = 0
        self._update_status()

    def _update_status(self) -> None:
        """Update the status bar with the currently selected account."""
        name, _ = self._accounts[self._account_idx]
        self.query_one("#status-bar", StatusBar).update(
            f"  📂  Account: [bold italic]{name}[/bold italic]"
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_cycle_account(self) -> None:
        """Cycle to the next account and refresh all data tables."""
        self._account_idx = (self._account_idx + 1) % len(self._accounts)
        _, account_id = self._accounts[self._account_idx]

        self._update_status()

        try:
            self.query_one("PositionsList").refresh_table(account_id)
        except Exception: pass

        try:
            self.query_one("TradesList").refresh_table(account_id)
        except Exception: pass

        try:
            self.query_one("TransactionsList").refresh_table(account_id)
        except Exception: pass


if __name__ == "__main__":
    app = MyFancyApp()
    app.run()