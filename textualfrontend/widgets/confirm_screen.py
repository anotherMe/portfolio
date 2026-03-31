from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Horizontal, Vertical


class ConfirmScreen(ModalScreen):
    """Generic yes/no confirmation modal. Dismisses with True on confirm, False on cancel."""

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    ConfirmScreen > Vertical {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $error;
        padding: 1 2;
    }
    ConfirmScreen #confirm-message {
        padding-bottom: 1;
    }
    ConfirmScreen #confirm-buttons {
        height: auto;
        margin-top: 1;
    }
    ConfirmScreen #confirm-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self._message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Delete", id="confirm-yes-btn", variant="error")
                yield Button("Cancel", id="confirm-no-btn")

    @on(Button.Pressed, "#confirm-yes-btn")
    def on_confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirm-no-btn")
    def on_cancel(self) -> None:
        self.dismiss(False)
