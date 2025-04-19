from textual.app import App
from textual.widgets import Header, Input, Footer, RichLog, DataTable, Button
from textual.containers import Container, Horizontal

from rich.text import Text
from rich.style import Style
from loguru import logger

from herding_cats_interactive.handlers.rich_log_handler import ExtendedRichLogHandler
from herding_cats_interactive.ui.components.catalogue_button import CatalogButton
from herding_cats_interactive.ui.components.command_button import CommandButton
from herding_cats_interactive.handlers.input_handler import InputHandler
from herding_cats_interactive.handlers.binding_hanlder import BindingHandler
from herding_cats_interactive.ui.styles.app_css import APP_CSS
from herding_cats_interactive.utils.constants import catalogues

from HerdingCats.session.session import CatSession, CatalogueType
from HerdingCats.explorer.explore import (
    CkanCatExplorer,
    OpenDataSoftCatExplorer,
    FrenchGouvCatExplorer,
)
from HerdingCats.loader.loader import CkanLoader, OpenDataSoftLoader, FrenchGouvLoader


class InteractiveCats(App):
    """Interactive terminal application for the HerdingCats library."""

    CSS = APP_CSS
    BINDINGS = [
        ("escape", "reset_app", "Reset App"),
        ("q", "quit", "Quit"),
        ("w", "show_catalogs", "Show Available Catalogs"),
        ("e", "show_commands", "Show Available Commands"),
        ("b", "previous_log", "Previous Log"),
        ("f", "next_log", "Next Log"),
        ("shift+left", "focus_log", "Focus RichLog"),
        ("shift+right", "focus_table", "Focus DataTable"),
        ("shift+down", "focus_input", "Focus Input"),
        ("shift+up", "unfocus_input", "Unfocus Input"),
    ]

    def __init__(self):
        super().__init__()
        self.session = None
        self.loader = None
        self.explorer = None
        self.logger_handler = None
        self.no_connection_status_button = None
        self.active_catalog_button = None
        self.rich_log = None
        self.data_table = None
        self.catalogs = catalogues
        self.input_handler = None

    def compose(self):
        """Create child widgets for the app."""
        yield Header(icon="+")
        yield Container(
            Horizontal(
                CatalogButton(self.catalogs),
                CommandButton(self.explorer),
                Button("Hot Key 1", id="hot-key-1", classes="hot-keys"),
                Button("Hot Key 2", id="hot-key-2", classes="hot-keys"),
                Button(
                    "Not Connected",
                    id="no-connection-status",
                    classes="no-connection-status",
                ),
                id="button-container",
            ),
            Horizontal(
                RichLog(highlight=True, markup=True, id="rich-log"),
                DataTable(id="data-table"),
                id="main-content",
            ),
            RichLog(highlight=True, markup=True, id="rich-log-2"),
            id="secondary-content",
        )
        yield Input(placeholder="Enter command (connect <catalog> to start)")
        yield Footer()

    def on_mount(self):
        """Initialize the application on startup."""
        # Set theme
        self.theme = "nord"

        # Set up logging handler
        rich_log = self.query_one(RichLog)
        rich_log.focus()
        self.logger_handler = ExtendedRichLogHandler(rich_log)

        # Remove default logger handlers and add our custom handler
        logger.remove()
        logger.add(self.logger_handler, format="{message}")

        # Set up Data Table
        self.data_table = self.query_one(DataTable)

        # Set up binding handler
        self.binding_handler = BindingHandler(self)

        # Set up input handler
        self.input_handler = InputHandler(self)

        # Set up no connection button
        self.no_connection_status_button = self.query_one("#no-connection-status")

        # Display welcome message
        self._show_welcome_message(rich_log)

    def reset_app(self):
        """Reset the app to its initial state."""
        # Close any existing session
        if hasattr(self, "session") and self.session:
            self.session.close_session()
            self.session = None

        if self.data_table:
            self.data_table.clear(columns=True)

        # Reset all variables to initial state
        self.explorer = None
        self.loader = None

        # Remove the connected catalog button if it exists
        if hasattr(self, "active_catalog_button") and self.active_catalog_button:
            self.active_catalog_button.remove()
            self.active_catalog_button = None
            button_container = self.query_one("#button-container")
            if not self.no_connection_status_button:
                self.no_connection_status_button = Button(
                    "Not Connected",
                    id="no-connection-status",
                    classes="no-connection-status",
                )
            button_container.mount(self.no_connection_status_button)

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
        welcome_text = Text(cat_art, style=Style(color="#5e81ac", bold=True))
        welcome_text.append(
            "Welcome to Interactive Cats\n \n", style=Style(color="white", bold=True)
        )
        welcome_text.append(
            "        Use 'connect <catalog>' to start!", style=Style(color="white")
        )
        rich_log.write(welcome_text)

    def clear_log(self):
        """Clear the log display."""
        if self.logger_handler:
            self.logger_handler.clear()

    def _show_welcome_message(self, rich_log: RichLog):
        """Display the welcome message in the RichLog widget."""
        cat_art = r"""
         /\_/\
        ( o.o )
        """

        welcome_text = Text(cat_art, style=Style(color="#5e81ac", bold=True))
        welcome_text.append(
            "Welcome to Interactive Cats\n \n", style=Style(color="white", bold=True)
        )
        welcome_text.append(
            "        Use 'connect <catalog>' to start!", style=Style(color="white")
        )
        rich_log.write(welcome_text)

    def on_catalog_button_catalog_list_requested(
        self, message: CatalogButton.CatalogListRequested
    ) -> None:
        """Handle the catalog list request."""
        rich_log = self.query_one(RichLog)
        rich_log.clear()
        rich_log.focus()
        rich_log.write(message.formatted_text)

    def on_command_button_command_list_requested(
        self, message: CommandButton.CommandListRequested
    ) -> None:
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

    def action_previous_log(self) -> None:
        """Show previous log entries."""
        if self.logger_handler:
            self.logger_handler.show_previous()

    def action_next_log(self) -> None:
        """Show next log entries."""
        if self.logger_handler:
            self.logger_handler.show_next()

    def format_catalog_list(self) -> Text:
        """Format the catalog list for display with rich text formatting."""
        # We can reuse the CatalogButton's formatting method
        catalog_button = self.query_one(CatalogButton)
        return catalog_button._format_catalog_list()

    def format_commands_list(self) -> Text:
        """Format the catalog list for display with rich text formatting."""
        # We can reuse the CatalogButton's formatting method
        command_button = self.query_one(CommandButton)
        return command_button._format_commands_list()

    async def on_input_submitted(self, message: Input.Submitted):
        """Handle input commands."""
        if self.input_handler:
            await self.input_handler.handle_command(message)
        else:
            logger.error("Input handler not initialized")

    async def create_explorer(self):
        """Create the appropriate explorer and loader based on catalog type."""
        if not self.session:
            return None, None

        catalog_type = self.session.catalogue_type
        match catalog_type:
            case CatalogueType.CKAN:
                return CkanCatExplorer(self.session), CkanLoader()
            case CatalogueType.OPENDATA_SOFT:
                return OpenDataSoftCatExplorer(self.session), OpenDataSoftLoader()
            case CatalogueType.GOUV_FR:
                return FrenchGouvCatExplorer(self.session), FrenchGouvLoader()

        return None, None

    async def _check_site_health(self) -> None:
        """Check site health."""
        if not self.explorer:
            return
        try:
            if isinstance(self.explorer, (CkanCatExplorer, OpenDataSoftCatExplorer)):
                self.explorer.check_site_health()
            elif isinstance(self.explorer, FrenchGouvCatExplorer):
                self.explorer.check_health_check()
        except Exception as e:
            logger.error(f"Error checking site health: {str(e)}")

    async def connect_to_catalog(self, catalog: str):
        """Core operation to connect to a catalog."""
        if catalog not in self.catalogs:
            return False, "Invalid catalog", None

        try:
            catalog_type, catalog_enum = self.catalogs[catalog]
            self.session = CatSession(catalog_enum)
            self.session.start_session()
            self.explorer, self.loader = await self.create_explorer()
            await self._check_site_health()

            command_button = self.query_one(CommandButton)
            command_button.update_explorer(self.explorer)
            return True, None, catalog_enum
        except Exception as e:
            return False, str(e), None

    async def close_catalog_connection(self):
        """Core operation to close a catalog connection."""
        if not self.session:
            return False, "No active connection"

        try:
            # Get info before closing
            catalog_name = (
                self.active_catalog_button.label.split(":")[-1]
                if self.active_catalog_button
                else "UNKNOWN"
            )
            catalog_type = self.session.catalogue_type.value

            # Close connection and cleanup
            self.session.close_session()
            self.session = None
            self.explorer = None
            if self.active_catalog_button:
                self.active_catalog_button.remove()

            # Update command button
            command_button = self.query_one(CommandButton)
            command_button.update_explorer(None)

            # Recreate and mount the no connection button if needed
            button_container = self.query_one("#button-container")
            if not self.no_connection_status_button:
                self.no_connection_status_button = Button(
                    "Not Connected",
                    id="no-connection-status",
                    classes="no-connection-status",
                )
            button_container.mount(self.no_connection_status_button)

            return True, catalog_name, catalog_type
        except Exception as e:
            return False, str(e), None

    def update_catalog_button(self, catalog: str):
        """Update UI after successful connection."""

        if self.session and self.no_connection_status_button:
            self.no_connection_status_button.remove()

        if self.active_catalog_button:
            self.active_catalog_button.remove()

        button_container = self.query_one("#button-container")
        self.active_catalog_button = Button(
            f"Connected: {catalog.upper()}", classes="connected-button"
        )
        button_container.mount(self.active_catalog_button)
