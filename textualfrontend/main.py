from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TabPane, TabbedContent, Select
from textual.containers import Horizontal
from textual import on
from api_service import get_accounts

# Import custom widgets
from tabs.instruments_tab import InstrumentsTab
from tabs.positions_tab import PositionsTab
from tabs.trades_tab import TradesTab
from tabs.transactions_tab import TransactionsTab
from tabs.accounts_tab import AccountsTab

class MyFancyApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Horizontal(id="header_container"):
            yield Select([], id="account_selector", allow_blank=True, prompt="All Accounts")
            
        yield Footer()

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

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        """Bind account data to selector and align correctly."""
        accounts = get_accounts()
        options = [(acc.name, str(acc.id)) for acc in accounts]
            
        selector = self.query_one("#account_selector", Select)
        selector.set_options(options)
        
        container = self.query_one("#header_container", Horizontal)
        container.styles.align = ("right", "middle")
        container.styles.height = "auto"
        container.styles.padding = (1, 1)

    @on(Select.Changed, "#account_selector")
    def on_account_select(self, event: Select.Changed) -> None:
        # None means blank ("All Accounts"), otherwise it's a specific account id string
        account_id = None if event.value is Select.BLANK else str(event.value)
        
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