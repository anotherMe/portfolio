from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal

from schemas.portfolio import PositionSummary
from .formatting import format_currency, format_currency_color, format_percent_color, format_date


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
