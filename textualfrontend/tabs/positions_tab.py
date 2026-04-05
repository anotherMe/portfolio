from textual.app import ComposeResult
from textual import on, work
from textual.widgets import DataTable, ContentSwitcher, Button, Static, Input, Select
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.screen import ModalScreen
from api_service import get_positions
from edit.position_edit import PositionEdit
from widgets.formatting import format_currency, format_currency_color, format_percent_color, format_date
from schemas.portfolio import PositionSummary

import logging
log = logging.getLogger(__name__)


class Filter():
    """A simple class to hold filter values for positions."""
    def __init__(self, instrument_name: str = "", isin: str = "", ticker: str = ""):
        self.instrument_name = instrument_name
        self.isin = isin
        self.ticker = ticker
        self.position_status = "all"  # "open", "closed", or "all"

class PositionFilter(ModalScreen[Filter]):
    """A collapsible widget for filtering positions."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    PositionFilter {
        align: center middle;
    }
    PositionFilter > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
    }
    PositionFilter #filter-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    PositionFilter #filter-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, current_filter: Filter | None = None, **kwargs):
        super().__init__(**kwargs)
        self._current_filter = current_filter or Filter()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Filter Positions", id="filter_title")
            yield Select(
                (("Open", "open"), ("Closed", "closed"), ("All", "all")),
                value=self._current_filter.position_status,
                id="filter_position_status"
            )
            yield Input(placeholder="Filter by Instrument Name", id="filter_instrument_name",
                        value=self._current_filter.instrument_name)
            yield Input(placeholder="Filter by Ticker", id="filter_ticker",
                        value=self._current_filter.ticker)
            yield Input(placeholder="Filter by ISIN", id="filter_isin",
                        value=self._current_filter.isin)
            with Horizontal(id="filter-buttons"):
                yield Button("Clear filters", id="clear_filters", variant="primary")
                yield Button("Apply filters", id="apply_filters", variant="primary")

    def on_input_submitted(self) -> None:
        self.action_apply()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply_filters":
            self.action_apply()
        elif event.button.id == "clear_filters":
            self.action_clear()

    def action_apply(self) -> None:
        f = Filter()
        f.instrument_name = self.query_one("#filter_instrument_name", Input).value
        f.isin = self.query_one("#filter_isin", Input).value
        f.ticker = self.query_one("#filter_ticker", Input).value
        f.position_status = self.query_one("#filter_position_status", Select).value
        self.dismiss(f)

    def action_clear(self) -> None:
        self.dismiss(Filter())

    def action_cancel(self) -> None:
        self.dismiss(self._current_filter)


class PositionDetails(Vertical):
    """A structured details panel showing all properties of the selected position."""

    DEFAULT_CSS = """
    PositionDetails {
        height: auto;
        border-top: solid $primary;
        padding: 0 1;
    }
    PositionDetails #pd-header {
        text-style: bold;
        height: 1;
        color: $text;
    }
    PositionDetails .pd-cols {
        height: auto;
    }
    PositionDetails .pd-row {
        height: 1;
        margin: 0;
    }
    PositionDetails .pd-label {
        color: $text-muted;
        width: 22;
    }
    PositionDetails .pd-value {
        width: 1fr;
    }
    PositionDetails .pd-col {
        width: 1fr;
        height: auto;
        padding: 0 2 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("— No position selected —", id="pd-header")
        with Horizontal(classes="pd-cols"):
            # Column 1: identity & dates
            with Vertical(classes="pd-col"):
                with Horizontal(classes="pd-row"):
                    yield Static("Position ID", classes="pd-label")
                    yield Static("", id="pd-position-id", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Account ID", classes="pd-label")
                    yield Static("", id="pd-account-id", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("ISIN", classes="pd-label")
                    yield Static("", id="pd-isin", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Currency", classes="pd-label")
                    yield Static("", id="pd-currency", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Status", classes="pd-label")
                    yield Static("", id="pd-status", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Opening date", classes="pd-label")
                    yield Static("", id="pd-opening-date", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Closing date", classes="pd-label")
                    yield Static("", id="pd-closing-date", classes="pd-value")
            # Column 2: cost & price
            with Vertical(classes="pd-col"):
                with Horizontal(classes="pd-row"):
                    yield Static("Remaining qty", classes="pd-label")
                    yield Static("", id="pd-qty", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Total invested", classes="pd-label")
                    yield Static("", id="pd-invested", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Cost basis", classes="pd-label")
                    yield Static("", id="pd-cost-basis", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Transactions", classes="pd-label")
                    yield Static("", id="pd-transactions", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Latest price", classes="pd-label")
                    yield Static("", id="pd-latest-price", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Latest price date", classes="pd-label")
                    yield Static("", id="pd-latest-price-date", classes="pd-value")
            # Column 3: PnL breakdown
            with Vertical(classes="pd-col"):
                with Horizontal(classes="pd-row"):
                    yield Static("Total PnL", classes="pd-label")
                    yield Static("", id="pd-pnl", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Total PnL %", classes="pd-label")
                    yield Static("", id="pd-pnl-pct", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Realized PnL", classes="pd-label")
                    yield Static("", id="pd-realized-pnl", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Realized PnL %", classes="pd-label")
                    yield Static("", id="pd-realized-pnl-pct", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Unrealized PnL", classes="pd-label")
                    yield Static("", id="pd-unrealized-pnl", classes="pd-value")
                with Horizontal(classes="pd-row"):
                    yield Static("Unrealized PnL %", classes="pd-label")
                    yield Static("", id="pd-unrealized-pnl-pct", classes="pd-value")

    def update(self, p: PositionSummary) -> None:
        ccy = p.instrument_currency
        self.query_one("#pd-header", Static).update(
            f"[bold]{p.instrument_name}[/bold]  [{p.instrument_ticker}]"
        )
        self.query_one("#pd-position-id", Static).update(str(p.position_id))
        self.query_one("#pd-account-id", Static).update(str(p.account_id))
        self.query_one("#pd-isin", Static).update(p.instrument_isin or "—")
        self.query_one("#pd-currency", Static).update(ccy or "—")
        self.query_one("#pd-status", Static).update(p.position_closed or "Open")
        self.query_one("#pd-opening-date", Static).update(format_date(p.opening_date))
        self.query_one("#pd-closing-date", Static).update(format_date(p.closing_date))
        self.query_one("#pd-qty", Static).update(str(p.remaining_quantity))
        self.query_one("#pd-invested", Static).update(format_currency(p.total_invested, ccy))
        self.query_one("#pd-cost-basis", Static).update(format_currency(p.remaining_cost_basis, ccy))
        self.query_one("#pd-transactions", Static).update(format_currency(p.transactions_amount, ccy))
        self.query_one("#pd-latest-price", Static).update(format_currency(p.latest_price, ccy))
        self.query_one("#pd-latest-price-date", Static).update(format_date(p.latest_price_date))
        self.query_one("#pd-pnl", Static).update(format_currency_color(p.pnl, ccy))
        self.query_one("#pd-pnl-pct", Static).update(format_percent_color(p.pnl_percent))
        self.query_one("#pd-realized-pnl", Static).update(format_currency_color(p.realized_pnl, ccy))
        self.query_one("#pd-realized-pnl-pct", Static).update(format_percent_color(p.realized_pnl_percent))
        self.query_one("#pd-unrealized-pnl", Static).update(format_currency_color(p.unrealized_pnl, ccy))
        self.query_one("#pd-unrealized-pnl-pct", Static).update(format_percent_color(p.unrealized_pnl_percent))

class PositionsList(Vertical):
    """Positions list (DataTable) on top half and the details view on the bottom half"""

    def compose(self) -> ComposeResult:

        table = DataTable(id="positions_table", cursor_type="row")
        yield table

        details = PositionDetails(id="position_details")
        yield details

    def on_mount(self) -> None:
        """Fetch and populate data when the tab is mounted."""

        self._positions: dict = {}
        table = self.query_one("#positions_table", DataTable)
        self.columns_to_show = [
            "instrument_name", "instrument_ticker",
            "opening_date", "total_invested", "latest_price",
            "remaining_quantity", "pnl",
            "pnl_percent", "closing_date"
        ]
        table.add_columns(*self.columns_to_show)
        self.refresh_table()

    @work(exclusive=True, thread=True)
    def refresh_table(self, account_id: int = None, filter: Filter = None) -> None:
        """Clear and repopulate the table filtered by account_id and optional filter."""

        try:
            table = self.query_one("#positions_table", DataTable)
            position_status = filter.position_status if filter else "all"
            positions = get_positions(
                account_id=account_id,
                include_open=(position_status in ["open", "all"]),
                include_closed=(position_status in ["closed", "all"]),
            )
            if filter:
                if filter.instrument_name:
                    positions = [p for p in positions if filter.instrument_name.lower() in p.instrument_name.lower()]
                if filter.ticker:
                    positions = [p for p in positions if filter.ticker.lower() in p.instrument_ticker.lower()]
                if filter.isin:
                    positions = [p for p in positions if filter.isin.lower() in p.instrument_isin.lower()]
            table.clear()
            if positions:
                self._populate_table(positions, table)
        except Exception as exc:
            log.error(f"Failed to load positions: {exc}")


    def _populate_table(self, positions, table):
        self._positions = {}
        for position in positions:
            self._positions[str(position.position_id)] = position

            row_data = position.model_dump(include=set(self.columns_to_show))
            
            row_data["opening_date"] = format_date(row_data["opening_date"])
            row_data["closing_date"] = format_date(row_data["closing_date"])
            row_data["pnl_percent"] = format_percent_color(row_data["pnl_percent"])
            row_data["total_invested"] = format_currency(row_data["total_invested"], position.instrument_currency)
            row_data["latest_price"] = format_currency(row_data["latest_price"], position.instrument_currency)
            row_data["pnl"] = format_currency_color(row_data["pnl"], position.instrument_currency)

            table.add_row(*[row_data[col] for col in self.columns_to_show], key=str(position.position_id))

class PositionsTab(Vertical):
    """The Positions tab content."""

    DEFAULT_CSS = """
    PositionsTab {
        height: 1fr;
    }
    PositionsList #positions_table {
        height: 2fr;
    }
    PositionsList #position_details {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("f", "filter", "Show Filters"),
        Binding("o", "cycle_status", "Cycle Status"),
    ]

    _STATUS_CYCLE = ["all", "open", "closed"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_account_id: int | None = None
        self._current_filter: Filter | None = None

    def reload(self, account_id: int | None) -> None:
        """Reload positions for a new account, keeping the current filter."""
        self._current_account_id = account_id
        self.query_one("#positions_list", PositionsList).refresh_table(
            self._current_account_id, self._current_filter
        )

    def compose(self) -> ComposeResult:
        with ContentSwitcher(id="positions_switcher", initial="positions_list"):
            yield PositionsList(id="positions_list")
            yield PositionEdit(id="position_edit")

    @on(DataTable.RowSelected, "#positions_table")
    def on_positions_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle a row being selected (e.g., by pressing Enter)."""
        position_id = event.row_key.value
        positions_list = self.query_one("#positions_list", PositionsList)
        position = positions_list._positions.get(position_id)

        if position:
            edit_widget = self.query_one("#position_edit", PositionEdit)
            edit_widget.load(position)

        switcher = self.query_one("#positions_switcher", ContentSwitcher)
        switcher.current = "position_edit"

    @on(DataTable.RowHighlighted, "#positions_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle a row being highlighted (e.g., by pressing arrow keys)."""
        row_key = event.row_key
        if row_key is None:
            return
        position = self.query_one("#positions_list", PositionsList)._positions.get(row_key.value)
        if position:
            self.query_one("#position_details", PositionDetails).update(position)

    @on(Button.Pressed, "#position-back-button")
    def show_position_list(self) -> None:
        """Triggered when the 'Back' button in positions tab is clicked."""
        self.action_back_to_list()

    def action_back_to_list(self) -> None:
        switcher = self.query_one("#positions_switcher", ContentSwitcher)
        if switcher.current != "positions_list":
            switcher.current = "positions_list"
            positions_list = self.query_one("#positions_list", PositionsList)
            positions_list.refresh_table(self._current_account_id, self._current_filter)
            positions_list.focus()

    def action_cycle_status(self) -> None:
        """Cycle the position_status filter through all → open → closed."""
        current = (self._current_filter.position_status if self._current_filter else "all")
        next_status = self._STATUS_CYCLE[
            (self._STATUS_CYCLE.index(current) + 1) % len(self._STATUS_CYCLE)
        ]
        if self._current_filter is None:
            self._current_filter = Filter()
        self._current_filter.position_status = next_status
        self.query_one("#positions_list", PositionsList).refresh_table(
            self._current_account_id, self._current_filter
        )

    def action_filter(self) -> None:
        """Show the filter modal."""
        def on_dismiss(filter: Filter) -> None:
            self._current_filter = filter
            self.query_one("#positions_list", PositionsList).refresh_table(
                self._current_account_id, self._current_filter
            )

        self.app.push_screen(PositionFilter(self._current_filter), on_dismiss)
