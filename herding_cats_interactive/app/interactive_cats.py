from textual.app import App
from textual.widgets import Header, Input, Footer, Button, RichLog
from textual.containers import Container, Horizontal
from rich.text import Text
from rich.style import Style
from loguru import logger

from herding_cats_interactive.ui.components.rich_log_handler import TextualRichLogHandler
from herding_cats_interactive.ui.styles.app_css import APP_CSS

class InteractiveCats(App):
    """Interactive terminal application for the HerdingCats library."""

    CSS = APP_CSS

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self):
        super().__init__()
        self.logger_handler = None

    def compose(self):
        """Create child widgets for the app."""
        yield Header(icon="+")
        yield Container(
            Horizontal(
                Button("Show Available Catalogs", id="show-catalogs"),
                Button("Show Commands", id="show-commands"),
                id="button-container"
            ),
            RichLog(highlight=True, markup=True)
        )
        yield Input(placeholder="Enter command (connect <catalog>, close, quit, home)")
        yield Footer()

    def on_mount(self):
        """Initialize the application on startup."""
        # Set theme
        self.theme = "dracula"

        # Set up logging with RichLog
        rich_log = self.query_one(RichLog)
        rich_log.focus()
        self.logger_handler = TextualRichLogHandler(rich_log)

        # Remove default logger handlers and add our custom handler
        logger.remove()
        logger.add(self.logger_handler, format="{message}")

        # Display welcome message
        self._show_welcome_message(rich_log)

    def _show_welcome_message(self, rich_log: RichLog):
        """Display the welcome message in the RichLog widget."""
        cat_art = r"""
         /\_/\
        ( o.o )
        """

        welcome_text = Text(cat_art, style=Style(color="blue", bold=True))
        welcome_text.append("Welcome to Interactive Cats\n \n", 
                        style=Style(color="green", bold=True))
        welcome_text.append(
            "        Use 'connect <catalog>' to start, or click 'Show Available Catalogs' to see options...", 
            style=Style(color="white")
        )
        rich_log.write(welcome_text)