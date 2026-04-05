from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Select, Static
from textual.containers import Horizontal, Vertical


class Filter:
    """A simple class to hold filter values for positions."""
    def __init__(self, instrument_name: str = "", isin: str = "", ticker: str = ""):
        self.instrument_name = instrument_name
        self.isin = isin
        self.ticker = ticker
        self.position_status = "all"  # "open", "closed", or "all"


class PositionFilter(ModalScreen[Filter]):
    """Modal for filtering the positions list."""

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
