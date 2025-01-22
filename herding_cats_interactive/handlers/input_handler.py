import asyncio
from textual.widgets import RichLog, Input
from rich.text import Text
from rich.style import Style

class InputHandler:
    """
    Input Handler acts like a traffic controller - routing commands to the right operations
    but not executing the operations itself.
    
    +-------------+     +--------------+     +------------------+
    |   Input     | --> |   Handler    | --> |  App Operations  |
    | (Commands)  |     | (Router/UI)  |     | (Business Logic) |
    +-------------+     +--------------+     +------------------+
    """

    def __init__(self, app):
        self.app = app
        self.rich_log = app.query_one(RichLog)
        self.input = app.query_one(Input)

    async def handle_command(self, message: Input.Submitted) -> None:
        """Main command handler."""
        # Split and clean input
        cmd = message.value.strip().split()
        if not cmd:
            return

        command = cmd[0].lower()
        self.app.clear_log()

        # Show loading animation
        await self.compose_loading_dots(message.value)
        
        self.input.value = ""
        self.app.clear_log()

        # Command routing
        command_handlers = {
            "connect": self._handle_connect,
            "close": self._handle_close,
            "quit": self._handle_quit
        }

        handler = command_handlers.get(command)
        if handler:
            await handler(cmd)
        else:
            # Handle unknown command
            self.rich_log.write(Text("❌ Unknown command\n", style=Style(color="red")))
            self.rich_log.write(Text("Available commands:\n", style=Style(color="yellow")))
            self.rich_log.write(self.app.format_commands_list())

    async def compose_loading_dots(self, command: str) -> None:
        """Display loading dots animation."""
        dots = ["   ", ".  ", ".. ", "..."]
        for dot in dots:
            text = Text()
            text.append("⚡ Please Wait! Processing Command: ", style=Style(color="cyan", italic=True))
            text.append(command, style=Style(color="white"))
            text.append(dot + "\n", style=Style(color="cyan"))
            self.app.clear_log()
            self.rich_log.write(text)
            await asyncio.sleep(0.1)

    async def _handle_connect(self, cmd: list) -> None:
        """Handle the connect command."""
        if len(cmd) < 2:
            self.rich_log.write(Text("Please Specify a Catalog\n", style=Style(color="yellow")))
            self.rich_log.write(self.app.format_catalog_list())
            return

        catalog = cmd[1].lower()
        success, error, catalog_enum = await self.app.connect_to_catalog(catalog)
        
        if not success:
            self.rich_log.write(Text(f"Invalid Catalog: {catalog}\n", style=Style(color="red")))
            self.rich_log.write(self.app.format_catalog_list())
            return

        # Update UI after successful connection
        self.app.update_catalog_button(catalog)
        
        catalog_type_name = self.app.session.catalogue_type
        self.rich_log.write(Text(f"Connected to {catalog} ({catalog_type_name})\n", 
                                style=Style(color="green")))
        self.rich_log.write(Text(f"URL: {catalog_enum.value}\n", style=Style(color="blue")))
        self.input.value = ""
        self.app.set_timer(3, self.app.clear_log)

    async def _handle_close(self, cmd: list) -> None:
        """Handle the close command."""

        if not self.app.session:
            self.rich_log.write(Text("No Active Connection...\n", style=Style(color="yellow")))
            self.input.value = ""
            self.rich_log.write(Text("Please Specify a Catalog\n", style=Style(color="yellow")))
            self.rich_log.write(self.app.format_catalog_list())
            return

        success, message, catalog_type = await self.app.close_catalog_connection()
        
        if not success:
            self.rich_log.write(Text(f"{message}\n", style=Style(color="yellow")))
            self.input.value = ""
            self.app.set_timer(1, self.app.clear_log)
            return

        # Remove button
        if self.app.active_catalog_button:
            self.app.active_catalog_button.remove()
            self.app.active_catalog_button = None

        # Show close message
        self.rich_log.write(Text(f"Connection Closed: {message} ({catalog_type})\n",
                            style=Style(color="green")))
        self.input.value = ""
        self.app.set_timer(1, self.app.clear_log)

    async def _handle_quit(self, cmd: list) -> None:
        """Handle the quit command."""
        if self.app.session:
            self.app.session.close_session()
        self.app.exit()

