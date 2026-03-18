from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, TabPane, TabbedContent

# Import custom widgets
from tabs.instruments_tab import InstrumentsTab
from tabs.positions_tab import PositionsTab

class MyFancyApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

        with TabbedContent(initial="positions"):

            with TabPane("Positions", id="positions"):
                yield PositionsTab()

            with TabPane("Instruments", id="instruments"):
                yield InstrumentsTab()

            with TabPane("Transactions", id="transactions"):
                yield Markdown("CHLOE")

            with TabPane("Trades", id="trades"):
                yield Markdown("PAUL")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Focus the data table when the Instruments tab is selected to enable keyboard navigation."""
        # if event.pane.id == "instruments":
        #     self.query_one(InstrumentsTab).query_one("DataTable").focus()
        # elif event.pane.id == "positions":
        #     self.query_one(PositionsTab).query_one("DataTable").focus()


if __name__ == "__main__":
    app = MyFancyApp()
    app.run()