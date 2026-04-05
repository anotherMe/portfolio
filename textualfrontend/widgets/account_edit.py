from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Horizontal, Vertical

from schemas.account import AccountCreate, AccountRead, AccountUpdate
import api_service

import logging
log = logging.getLogger(__name__)


class AccountActionsModal(ModalScreen):
    """Modal shown when an account row is selected."""

    BINDINGS = [("escape", "dismiss", "Cancel")]

    DEFAULT_CSS = """
    AccountActionsModal {
        align: center middle;
    }
    AccountActionsModal > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }
    AccountActionsModal #modal-info {
        padding-bottom: 1;
    }
    AccountActionsModal #modal-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    AccountActionsModal #modal-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, account: AccountRead, **kwargs):
        super().__init__(**kwargs)
        self._account = account

    def compose(self) -> ComposeResult:
        a = self._account
        with Vertical():
            yield Static(
                f"[bold]{a.name}[/bold]"
                + (f"  [dim]{a.description}[/dim]" if a.description else ""),
                id="modal-info",
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Cancel", id="modal-cancel-btn")
                yield Button("Edit", id="modal-edit-btn", variant="warning")
                yield Button("Delete", id="modal-delete-btn", variant="error")

    @on(Button.Pressed, "#modal-cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#modal-edit-btn")
    def on_edit(self) -> None:
        self.dismiss("edit")

    @on(Button.Pressed, "#modal-delete-btn")
    def on_delete(self) -> None:
        self.dismiss("delete")


class AccountEditModal(ModalScreen):
    """Modal form for editing an Account."""

    DEFAULT_CSS = """
    AccountEditModal {
        align: center middle;
    }
    AccountEditModal > Vertical {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    AccountEditModal Label {
        margin-top: 1;
    }
    AccountEditModal #form-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }
    AccountEditModal #form-buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, account: AccountRead, **kwargs):
        super().__init__(**kwargs)
        self._account = account

    def compose(self) -> ComposeResult:
        a = self._account
        with Vertical():
            yield Static(f"Edit Account: [bold]{a.name}[/bold]")
            yield Label("Name *")
            yield Input(value=a.name or "", id="field-name")
            yield Label("Description")
            yield Input(value=a.description or "", id="field-description")
            with Horizontal(id="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save", id="btn-save", variant="success")

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        self._do_save()

    @work(thread=True)
    def _do_save(self) -> None:
        data = AccountUpdate(
            name=self.query_one("#field-name", Input).value or None,
            description=self.query_one("#field-description", Input).value or None,
        )
        try:
            result = api_service.update_account(self._account.id, data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to update account {self._account.id}: {exc}")
            self.app.call_from_thread(self.dismiss, None)


class AccountCreateModal(ModalScreen):
    """Modal form for creating a new Account."""

    DEFAULT_CSS = AccountEditModal.DEFAULT_CSS.replace("AccountEditModal", "AccountCreateModal")

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Add Account")
            yield Label("Name *")
            yield Input(placeholder="Account name", id="field-name")
            yield Label("Description")
            yield Input(placeholder="Optional description", id="field-description")
            with Horizontal(id="form-buttons"):
                yield Button("Cancel", id="btn-cancel")
                yield Button("Save", id="btn-save", variant="success")

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def on_save(self) -> None:
        self._do_save()

    @work(thread=True)
    def _do_save(self) -> None:
        data = AccountCreate(
            name=self.query_one("#field-name", Input).value or "",
            description=self.query_one("#field-description", Input).value or None,
        )
        try:
            result = api_service.create_account(data)
            self.app.call_from_thread(self.dismiss, result)
        except Exception as exc:
            log.error(f"Failed to create account: {exc}")
            self.app.call_from_thread(self.dismiss, None)
