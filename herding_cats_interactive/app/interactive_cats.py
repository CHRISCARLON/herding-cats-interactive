from textual.app import App
from textual.widgets import Header, Input, Footer, Button, RichLog, DataTable
from textual.containers import Container, Horizontal
from rich.text import Text
from rich.style import Style
from loguru import logger

from herding_cats_interactive.ui.components.rich_log_handler import TextualRichLogHandler
from herding_cats_interactive.ui.styles.app_css import APP_CSS
from herding_cats_interactive.ui.components.catalogue_button import CatalogButton
from herding_cats_interactive.ui.components.command_button import CommandButton
from herding_cats_interactive.utils.constants import catalogues

class InteractiveCats(App):
    """Interactive terminal application for the HerdingCats library."""

    CSS = APP_CSS
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("w", "list", "List available catalogs"),
        ("e", "list_commands", "List available commands")
    ]

    def __init__(self):
        super().__init__()
        self.session = None
        self.loader = None
        self.explorer = None
        self.logger_handler = None
        self.active_catalog_button = None
        self.rich_log = None
        self.data_table = None
        self.catalogs = catalogues

    def compose(self):
        """Create child widgets for the app."""
        yield Header(icon="+")
        yield Container(
            Horizontal(
                CatalogButton(self.catalogs),
                CommandButton(self.explorer),
                id="button-container"
            ),
            Horizontal(
                RichLog(highlight=True, markup=True, id="rich-log"),
                DataTable(id="data-table"),
                id="main-content"
            )
        )
        yield Input(placeholder="Enter command (connect <catalog>, close, quit, home, ...)")
        yield Footer()

    def on_mount(self):
        """Initialize the application on startup."""
        # Set theme
        self.theme = "dracula"

        # Set up logging with RichLog
        rich_log = self.query_one(RichLog)
        rich_log.focus()
        self.logger_handler = TextualRichLogHandler(rich_log)

        # Set up Data Table
        self.query_one(DataTable)

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

    def on_catalog_button_catalog_list_requested(self, message: CatalogButton.CatalogListRequested) -> None:
        """Handle the catalog list request."""
        rich_log = self.query_one(RichLog)
        rich_log.clear() 
        rich_log.focus()
        rich_log.write(message.formatted_text)

    def on_command_button_command_list_requested(self, message: CommandButton.CommandListRequested) -> None:
        """Handle the command list request."""
        rich_log = self.query_one(RichLog)
        rich_log.clear() 
        rich_log.focus()
        rich_log.write(message.formatted_text)

    def action_list(self) -> None:
        """Handle the 'w' key binding to list available catalogs."""
        self.query_one(CatalogButton)
        
    def action_list_commands(self) -> None:
        """Handle the 'e' key binding to list available commands."""
        self.query_one(CommandButton)