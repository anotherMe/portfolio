from pathlib import Path
from typing import Callable, Iterable, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label, Static


class FilteredDirectoryTree(DirectoryTree):
    """A DirectoryTree that only shows directories and files matching given extensions."""

    def __init__(self, path: str | Path, extensions: Iterable[str] = (), **kwargs):
        super().__init__(path, **kwargs)
        self._extensions = tuple(ext.lower() for ext in extensions)

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        if not self._extensions:
            return paths
        return [
            p for p in paths
            if p.is_dir() or p.suffix.lower() in self._extensions
        ]


class FilePickerModal(ModalScreen[Optional[Path]]):
    """A reusable modal screen for browsing and selecting a file.

    Dismisses with the selected ``Path``, or ``None`` if cancelled.

    Usage::

        def on_confirm(path: Path | None) -> None:
            if path:
                ...

        self.app.push_screen(
            FilePickerModal(title="Select JSON file", extensions=[".json"]),
            on_confirm,
        )
    """

    DEFAULT_CSS = """
    FilePickerModal {
        align: center middle;
    }

    FilePickerModal > Vertical {
        width: 80;
        height: 30;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    FilePickerModal #picker-title {
        text-style: bold;
        margin-bottom: 1;
    }

    FilePickerModal FilteredDirectoryTree {
        height: 1fr;
        border: solid $primary;
    }

    FilePickerModal #selected-path {
        height: 1;
        margin-top: 1;
        color: $text-muted;
        overflow: hidden;
    }

    FilePickerModal Horizontal {
        height: auto;
        align-horizontal: right;
        margin-top: 1;
    }

    FilePickerModal Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        title: str = "Select a file",
        start_path: str | Path = Path.home(),
        extensions: Iterable[str] = (),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._title = title
        self._start_path = Path(start_path)
        self._extensions = list(extensions)
        self._selected: Optional[Path] = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title, id="picker-title")
            yield FilteredDirectoryTree(
                self._start_path,
                extensions=self._extensions,
                id="dir-tree",
            )
            yield Static("No file selected", id="selected-path")
            with Horizontal():
                yield Button("Confirm", id="confirm", variant="primary", disabled=True)
                yield Button("Cancel", id="cancel", variant="default")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self._selected = event.path
        self.query_one("#selected-path", Static).update(str(event.path))
        self.query_one("#confirm", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(self._selected)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
