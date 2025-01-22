from textual.app import App
from textual.widgets import Header, Input, Footer, RichLog, DataTable
from textual.containers import Container, Horizontal
from rich.text import Text
from rich.style import Style
from loguru import logger

from herding_cats_interactive.ui.components.rich_log_handler import TextualRichLogHandler
from herding_cats_interactive.ui.components.catalogue_button import CatalogButton
from herding_cats_interactive.ui.components.command_button import CommandButton
from herding_cats_interactive.utils.binding_hanlder import BindingHandler
from herding_cats_interactive.ui.styles.app_css import APP_CSS
from herding_cats_interactive.utils.constants import catalogues

class InteractiveCats(App):
    """Interactive terminal application for the HerdingCats library."""

    CSS = APP_CSS
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "reset_app", "Reset App"),
        ("w", "show_catalogs", "Show Available Catalogs"),
        ("e", "show_commands", "Show Available Commands"),
        ("shift+left", "focus_log", "Focus RichLog"),
        ("shift+right", "focus_table", "Focus DataTable"),
        ("shift+down", "focus_input", "Focus Input"),
        ("shift+up", "unfocus_input", "Unfocus Input")
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
        yield Input(placeholder="Enter command (connect <catalog> to start)")
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

        # Set up binding handler    
        self.binding_handler = BindingHandler(self)

        # Remove default logger handlers and add our custom handler
        logger.remove()
        logger.add(self.logger_handler, format="{message}")

        # Display welcome message
        self._show_welcome_message(rich_log)

    def reset_app(self):
        """Reset the app to its initial state."""
        # Close any existing session
        if hasattr(self, 'session') and self.session:
            self.session.close_session()
            self.session = None

        # Reset all variables to initial state
        self.explorer = None
        self.loader = None

        # Remove the connected catalog button if it exists
        if hasattr(self, 'active_catalog_button') and self.active_catalog_button:
            self.active_catalog_button.remove()
            self.active_catalog_button = None

        # Clear the input
        self.query_one(Input).value = ""

        # Clear and reset the log
        rich_log = self.query_one(RichLog)
        rich_log.clear()
        
        # Show welcome message again
        cat_art = r"""
         /\_/\
        ( o.o )
        """
        welcome_text = Text(cat_art, style=Style(color="blue", bold=True))
        welcome_text.append("Welcome to Interactive Cats\n \n", style=Style(color="green", bold=True))
        welcome_text.append("        Use 'connect <catalog>' to start, or click 'Show Available Catalogs' to see options...",
                        style=Style(color="white"))
        rich_log.write(welcome_text)

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
    
    def action_show_catalogs(self) -> None:
        self.binding_handler.handle_action("show_catalogs")

    def action_show_commands(self) -> None:
        self.binding_handler.handle_action("show_commands")

    def action_focus_log(self) -> None:
        """Focus the RichLog widget."""
        self.binding_handler.handle_action("focus_log")

    def action_focus_table(self) -> None:
        """Focus the DataTable widget."""
        self.binding_handler.handle_action("focus_table")

    def action_focus_input(self) -> None:
        """Focus the Input widget."""
        self.binding_handler.handle_action("focus_input")

    def action_unfocus_input(self) -> None:
        """Unfocus the Input widget."""
        self.binding_handler.handle_action("unfocus_input")

    def action_reset_app(self) -> None:
        """Reset the app to its initial state."""
        self.binding_handler.handle_action("reset_app")