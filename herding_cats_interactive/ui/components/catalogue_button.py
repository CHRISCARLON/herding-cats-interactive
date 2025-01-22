from textual.events import Key
from textual.widgets import Button
from textual.message import Message
from rich.text import Text
from rich.style import Style
from typing import Dict, Tuple, Any

class CatalogButton(Button):
    """A button component that handles displaying catalog information."""
    
    class CatalogListRequested(Message):
        """Event sent when catalog list should be displayed."""
        def __init__(self, formatted_text: Text) -> None:
            self.formatted_text = formatted_text
            super().__init__()

    def __init__(self, catalogs: Dict[str, Tuple[str, Any]], **kwargs):
        """Initialize the catalog button.
        
        Args:
            catalogs: Dictionary of catalogs where key is the name and value is a tuple of (type, url)
        """
        super().__init__("Show Available Catalogs", **kwargs)
        self.catalogs = catalogs

    def _format_catalog_list(self) -> Text:
        """Format the catalog list for display with rich text formatting."""
        output = Text("Available Catalogs:\n\n", style=Style(color="green", bold=True))

        # Group catalogs by type
        ckan_catalogs = [name for name, (type_, _) in self.catalogs.items() if type_ == 'ckan']
        ods_catalogs = [name for name, (type_, _) in self.catalogs.items() if type_ == 'opendatasoft']
        fr_catalogs = [name for name, (type_, _) in self.catalogs.items() if type_ == 'french_gov']

        output.append("CKAN Catalogs:\n", style=Style(color="cyan", bold=True))
        for name in sorted(ckan_catalogs):
            url = self.catalogs[name][1].value
            output.append(f"- {name}: ", style=Style(color="yellow"))
            output.append(f"{url}\n", style=Style(color="white"))

        output.append("\nOpenDataSoft Catalogs:\n", style=Style(color="cyan", bold=True))
        for name in sorted(ods_catalogs):
            url = self.catalogs[name][1].value
            output.append(f"- {name}: ", style=Style(color="yellow"))
            output.append(f"{url}\n", style=Style(color="white"))

        output.append("\nFrench Government Catalogs:\n", style=Style(color="cyan", bold=True))
        for name in sorted(fr_catalogs):
            url = self.catalogs[name][1].value
            output.append(f"- {name}: ", style=Style(color="yellow"))
            output.append(f"{url}\n", style=Style(color="white"))

        return output

    def on_click(self) -> None:
        """Handle button click by emitting a CatalogListRequested message."""
        formatted_text = self._format_catalog_list()
        self.post_message(self.CatalogListRequested(formatted_text))