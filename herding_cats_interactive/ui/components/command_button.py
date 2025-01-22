from textual.widgets import Button
from textual.message import Message

from rich.text import Text
from rich.style import Style

from typing import Optional

from HerdingCats.explorer.cat_explore import CkanCatExplorer, OpenDataSoftCatExplorer, FrenchGouvCatExplorer

class CommandButton(Button):
    """A button component that handles displaying command information."""
    
    class CommandListRequested(Message):
        """Event sent when command list should be displayed."""
        def __init__(self, formatted_text: Text) -> None:
            self.formatted_text = formatted_text
            super().__init__()

    def __init__(self, explorer: Optional[CkanCatExplorer | OpenDataSoftCatExplorer | FrenchGouvCatExplorer] = None, **kwargs):
        """Initialize the command button."""
        super().__init__("Show Commands", **kwargs)
        self.explorer = explorer

    def update_explorer(self, explorer: Optional[CkanCatExplorer | OpenDataSoftCatExplorer | FrenchGouvCatExplorer] = None) -> None:
        """Update the explorer and refresh the button's command list."""
        self.explorer = explorer

    def _format_commands_list(self) -> Text:
        """Format the available commands list with rich text formatting."""
        output = Text()

        # Helper functions
        def _add_command_section(commands: list[tuple[str, str]], header: str | None = None):
            if header:
                output.append(f"{header}\n", style=Style(color="yellow", bold=True))
            for cmd, desc in commands:
                output.append(f"  {cmd:<25}", style=Style(color="cyan", bold=True))
                output.append(f": {desc}\n", style=Style(color="white"))

        def _add_examples(examples: list[tuple[str, str]]):
            output.append("\nExample Usage:\n", style=Style(color="green", bold=True))
            output.append("--------------\n")
            for cmd, desc in examples:
                output.append(f"  {cmd}", style=Style(color="cyan"))
                output.append(f"     : {desc}\n", style=Style(color="white"))

        # Basic commands section
        output.append("Basic Commands:\n", style=Style(color="green", bold=True))
        output.append("-------------\n")
        _add_command_section([
            ("connect <catalog>", "Connect to a specific data catalog"),
            ("close", "Close the current connection"),
            ("quit", "Exit the application")
        ])

        # Catalog-specific commands using match statement
        match self.explorer:
            case CkanCatExplorer():
                output.append("\nCatalog-Specific Commands:\n", style=Style(color="green", bold=True))
                output.append("------------------------\n")

                _add_command_section([
                    ("list packages", "Show all available packages"),
                    ("package info <name>", "Show detailed information about a specific package"),
                    ("search <query> <rows>", "Search packages with query and limit results"),
                    ("list orgs", "Show all organizations in the catalog"),
                    ("load <id> <format>", "Load a data sample into a DataFrame with an optional format specified")
                ], "CKAN Commands:")

                _add_examples([
                    ("search police 10", "Search for 'police' datasets, limit to 10 results"),
                    ("package info london-crime", "Show details for package named 'london-crime'")
                ])

            case OpenDataSoftCatExplorer():
                output.append("\nCatalog-Specific Commands:\n", style=Style(color="green", bold=True))
                output.append("------------------------\n")

                _add_command_section([
                    ("list datasets", "Show all available datasets"),
                    ("dataset info <id>", "Show detailed information about a specific dataset"),
                    ("dataset export <id>", "Show available export formats for a dataset"),
                    ("load <id> <format> <api-key>", "Load a data sample into a DataFrame. Api-key is optional.")
                ], "OpenDataSoft Commands:")

                _add_examples([
                    ("dataset info power-consumption", "Show details for dataset 'power-consumption'"),
                    ("dataset export energy-data", "Show export formats for 'energy-data'")
                ])

            case FrenchGouvCatExplorer():
                output.append("\nCatalog-Specific Commands:\n", style=Style(color="green", bold=True))
                output.append("------------------------\n")

                _add_command_section([
                    ("list datasets", "Show all available datasets"),
                    ("dataset meta <dataset_id>", "Show metadata for a specific dataset"),
                    ("resource meta <dataset_id>", "Show metadata for a specific resource"),
                    ("list orgs", "Show all organizations in the catalog"),
                    ("load <id> <format>", "Load a data sample into a DataFrame.")
                ], "French Government Commands:")

                _add_examples([
                    ("dataset meta 123abc", "Show metadata for dataset with ID '123abc'"),
                    ("resource meta 123abc res456", "Show metadata for resource 'res456' in dataset '123abc'")
                ])

            case None:
                output.append("\nYou Are Not Connected to a Catalog:\n", style=Style(color="yellow", bold=True))
                output.append("Use 'show catalogs' to see available catalogs, then connect to one:\n",
                            style=Style(color="white"))
                _add_examples([
                    ("connect london-datastore", "Connect to the London Data Store"),
                    ("connect uk-power-networks", "Connect to the UKPN Data Store")
                ])

            case _:  # Catch-all case for unknown explorer types
                output.append("\nUnknown explorer type\n", style=Style(color="red", bold=True))

        return output

    def on_click(self) -> None:
        """Handle button click by emitting a CommandListRequested message."""
        formatted_text = self._format_commands_list()
        self.post_message(self.CommandListRequested(formatted_text))