from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MixedLayout(App):
    
    CSS = """
    #fixed-header {
        height: 1;
        background: blue;
    }
    .flexible-body {
        height: 1fr;
        background: green;
        border: solid white;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        yield Static("I take half of what's left", classes="flexible-body")
        yield Static("I take the other half", classes="flexible-body")
        yield Static("I am exactly 1 character high", id="fixed-header")

if __name__ == "__main__":
    MixedLayout().run()