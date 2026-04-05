from textual.app import ComposeResult
from textual import on
from textual.binding import Binding
from textual.widgets import DataTable, ContentSwitcher, Button
from textual.containers import Vertical

from .positions_filter import Filter, PositionFilter
from .positions_list import PositionsList
from .positions_details import PositionDetails
from .position_edit import PositionEdit

import logging
log = logging.getLogger(__name__)


class PositionsTab(Vertical):
    """The Positions tab: list view with inline details, switches to a full edit view."""

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
        """Open the position edit view when a row is selected."""
        position_id = event.row_key.value
        positions_list = self.query_one("#positions_list", PositionsList)
        position = positions_list._positions.get(position_id)

        if position:
            self.query_one("#position_edit", PositionEdit).load(position)

        self.query_one("#positions_switcher", ContentSwitcher).current = "position_edit"

    @on(DataTable.RowHighlighted, "#positions_table")
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Update the details panel as the cursor moves."""
        row_key = event.row_key
        if row_key is None:
            return
        position = self.query_one("#positions_list", PositionsList)._positions.get(row_key.value)
        if position:
            self.query_one("#position_details", PositionDetails).update(position)

    @on(Button.Pressed, "#position-back-button")
    def show_position_list(self) -> None:
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
