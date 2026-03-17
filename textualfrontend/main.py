from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Footer, Header, Markdown, TabPane, TabbedContent
from api_service import get_positions, get_instruments
from textual.widgets import DataTable


class MyFancyApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

        with TabbedContent(initial="instruments"):
            
            with TabPane("Instruments", id="instruments"):
                
                table = DataTable()
                table.id = "instruments_table"
                table.cursor_type = "row"

                instruments = get_instruments()

                columns_to_show = {"name", "ticker", "category", "currency"}
                table.add_columns(*instruments[0].model_dump(include=columns_to_show).keys())
                for instrument in instruments:
                    table.add_row(*instrument.model_dump(include=columns_to_show).values(), key=str(instrument.id))
                
                yield table

            with TabPane("Positions", id="positions"):
                
                table = DataTable()
                table.id = "positions_table"
                table.cursor_type = "row"

                positions = get_positions()

                columns_to_show = {"instrument_name", "instrument_isin", "instrument_ticker", "opening_date", "total_invested", "latest_price", "latest_price_date", "transactions_amount", "closing_date", "remaining_quantity", "remaining_cost_basis", "realized_pnl", "unrealized_pnl", "realized_pnl_percent", "unrealized_pnl_percent", "pnl", "pnl_percent", "position_closed"}
                table.add_columns(*positions[0].model_dump(include=columns_to_show).keys())
                for position in positions:
                    table.add_row(*position.model_dump(include=columns_to_show).values(), key=str(position.position_id))
                
                yield table

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
        if event.pane.id == "instruments":
            self.query_one(DataTable).focus()

    @on(DataTable.RowSelected, "#positions_table")
    def on_positions_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        position_id = row_key.value
        row_data = table.get_row(row_key)
        self.notify(f"Selected position ID {position_id} with data: {row_data}")

    @on(DataTable.RowSelected, "#instruments_table")
    def on_instruments_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        table = event.data_table
        row_key = event.row_key
        instrument_id = row_key.value
        row_data = table.get_row(row_key)
        self.notify(f"Selected instrument ID {instrument_id} with data: {row_data}")


if __name__ == "__main__":
    app = MyFancyApp()
    app.run()