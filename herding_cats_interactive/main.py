from textual.app import App
from textual.widgets import Header, Input, Footer, Button, RichLog, DataTable
from textual.containers import Container, Horizontal
from HerdingCats.session.cat_session import CatSession, CatalogueType
from HerdingCats.endpoints.api_endpoints import (
    CkanDataCatalogues,
    OpenDataSoftDataCatalogues,
    FrenchGouvCatalogue
)
from HerdingCats.explorer.cat_explore import CkanCatExplorer, OpenDataSoftCatExplorer, FrenchGouvCatExplorer
from HerdingCats.data_loader.data_loader import CkanCatResourceLoader, OpenDataSoftResourceLoader

from loguru import logger
from rich.text import Text
from rich.console import Console
from rich.style import Style

class TextualRichLogHandler:
    """Custom logger handler that sends output to a Textual RichLog widget."""

    def __init__(self, log_display: RichLog):
        self.log_display = log_display
        # Define styles for different log levels
        self.styles = {
            "INFO": Style(color="blue"),
            "SUCCESS": Style(color="green"),
            "WARNING": Style(color="yellow"),
            "ERROR": Style(color="red"),
            "DEBUG": Style(color="cyan")
        }

    def write(self, message):
        """Write a message to the rich log display."""
        if hasattr(message, "record"):
            level = message.record["level"].name
            style = self.styles.get(level, Style())
            text = Text(str(message).strip() + "\n", style=style)
            self.log_display.write(text)
        else:
            self.log_display.write(Text(str(message).strip() + "\n"))

    def clear(self):
        """Clear the log display."""
        self.log_display.clear()

    def flush(self):
        """Required for handler interface."""
        pass

class InteractiveCats(App):
    """Create an interactive terminal session with the HerdingCats library."""

    CSS = """
    #button-container {
        height: auto;
        align: left middle;
        padding: 1 2;
    }

    #button-container Button {
        background: $primary;
        color: $text;
        margin: 0 1;
        padding: 0 2;
        height: 3;
        border: heavy $primary;
    }

    #button-container Button:hover {
        background: $primary-darken-2;
        border: heavy $primary-darken-2;
    }

    RichLog {
        height: 1fr;
        min-height: 25;
        border: solid $panel;
        background: $surface;
        color: $text;
        margin: 1 1;
    }

    Screen {
        overflow: hidden;
    }

    .active-catalog {
        background: $boost;
        color: $text;
        margin-left: 2;
        border: none;
    }
    """

    def __init__(self):
        super().__init__()
        self.session = None
        self.loader = None
        self.explorer = None
        self.logger_handler = None
        self.active_catalog_button = None
        self.rich_log = None
        self.data_table = None
        self.catalogs = {
            # CKAN Catalogs
            'london': ('ckan', CkanDataCatalogues.LONDON_DATA_STORE),
            'uk-gov': ('ckan', CkanDataCatalogues.UK_GOV),
            'subak': ('ckan', CkanDataCatalogues.SUBAK),
            'humanitarian': ('ckan', CkanDataCatalogues.HUMANITARIAN_DATA_STORE),
            'open-africa': ('ckan', CkanDataCatalogues.OPEN_AFRICA),

            # OpenDataSoft Catalogs
            'uk-power': ('opendatasoft', OpenDataSoftDataCatalogues.UK_POWER_NETWORKS),
            'infrabel': ('opendatasoft', OpenDataSoftDataCatalogues.INFRABEL),
            'paris': ('opendatasoft', OpenDataSoftDataCatalogues.PARIS),
            'toulouse': ('opendatasoft', OpenDataSoftDataCatalogues.TOULOUSE),
            'elia-energy': ('opendatasoft', OpenDataSoftDataCatalogues.ELIA_BELGIAN_ENERGY),
            'edf-energy': ('opendatasoft', OpenDataSoftDataCatalogues.EDF_ENERGY),
            'cadent-gas': ('opendatasoft', OpenDataSoftDataCatalogues.CADENT_GAS),
            'grd-france': ('opendatasoft', OpenDataSoftDataCatalogues.GRD_FRANCE),

            # French Government Catalog
            'french-gov': ('french_gov', FrenchGouvCatalogue.GOUV_FR)
        }

    def compose(self):
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Horizontal(
                Button("Show Available Catalogs", id="show-catalogs"),
                Button("Show Commands", id="show-commands"),
                id="button-container"
            ),
            RichLog(highlight=True, markup=True)
        )
        yield Input(placeholder="Enter command (connect <catalog>, close, quit)")
        yield Footer()

    def on_mount(self):
        """Set up logging and theme when the app starts."""
        # Set theme
        self.theme = "flexoki"

        # Set up logging with RichLog
        self.rich_log = self.query_one(RichLog)
        self.rich_log.focus()
        self.logger_handler = TextualRichLogHandler(self.rich_log)  # Correct reference

        # Remove default logger handlers
        logger.remove()
        # Add our custom handler
        logger.add(self.logger_handler, format="{message}")

        # Welcome message with rich formatting
        welcome_text = Text("Welcome to Interactive Cats 🐈‍⬛\n", style=Style(color="green", bold=True))
        welcome_text.append("Use 'connect <catalog>' to start, or click 'Show Available Catalogs to see options...", style=Style(color="blue"))
        self.rich_log.write(welcome_text)

    def toggle_to_data_table(self, df):
        """Unmount the RichLog and mount the DataTable with provided dataframe."""
        if self.rich_log:
            self.rich_log.remove()  # Unmount RichLog
        self.data_table = DataTable()  # Create a new DataTable
        self.data_table.add_columns(*df.columns)

        # Add data to DataTable
        for i, row in enumerate(df.iter_rows(named=True)):
            if i >= 15:
                break
            self.data_table.add_row(*[str(val) for val in row])

        self.mount(self.data_table)  # Mount DataTable

    def toggle_to_rich_log(self):
        """Unmount the DataTable and re-mount the RichLog."""
        if self.data_table:
            self.data_table.remove()  # Unmount the DataTable

        if self.rich_log is not None:
            self.mount(self.rich_log)  # Re-mount RichLog safely
        else:
            logger.error("RichLog is not initialized, cannot mount.")

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

    def create_explorer(self):
        """Create the appropriate explorer and loader based on catalog type."""
        if not self.session:
            return None, None

        catalog_type = self.session.get_catalogue_type()
        explorer = None
        loader = None

        match catalog_type:
            case CatalogueType.CKAN:
                explorer = CkanCatExplorer(self.session)
                loader = CkanCatResourceLoader()
            case CatalogueType.OPENDATA_SOFT:
                explorer = OpenDataSoftCatExplorer(self.session)
                loader = OpenDataSoftResourceLoader()
            case CatalogueType.GOUV_FR:
                explorer = FrenchGouvCatExplorer(self.session)
                # Add the appropriate loader for FrenchGouv if available
                # loader = FrenchGouvResourceLoader()

        return explorer, loader

    def format_catalog_list(self) -> Text:
        """Format the catalog list for display with rich text formatting."""
        output = Text("Available Catalogs:\n\n", style=Style(bold=True))

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

    def format_commands_list(self) -> Text:
        """Format the available commands list with rich text formatting."""
        output = Text()

        # Basic commands section
        output.append("Basic Commands:\n", style=Style(color="green", bold=True))
        output.append("-------------\n")
        basic_commands = [
            ("connect <catalog>", "Connect to a specific data catalog"),
            ("close", "Close the current connection"),
            ("quit", "Exit the application")
        ]
        for cmd, desc in basic_commands:
            output.append(f"  {cmd:<25}", style=Style(color="cyan", bold=True))
            output.append(f": {desc}\n", style=Style(color="white"))

        # If connected, show catalog-specific commands
        if self.explorer:
            output.append("\nCatalog-Specific Commands:\n", style=Style(color="green", bold=True))
            output.append("------------------------\n")

            if isinstance(self.explorer, CkanCatExplorer):
                output.append("CKAN Commands:\n", style=Style(color="yellow", bold=True))
                ckan_commands = [
                    ("list packages", "Show all available packages"),
                    ("package info <name>", "Show detailed information about a specific package"),
                    ("search <query> <rows>", "Search packages with query and limit results"),
                    ("list orgs", "Show all organizations in the catalog")
                ]
                for cmd, desc in ckan_commands:
                    output.append(f"  {cmd:<25}", style=Style(color="cyan", bold=True))
                    output.append(f": {desc}\n", style=Style(color="white"))

            elif isinstance(self.explorer, OpenDataSoftCatExplorer):
                output.append("OpenDataSoft Commands:\n", style=Style(color="yellow", bold=True))
                ods_commands = [
                    ("list datasets", "Show all available datasets"),
                    ("dataset info <id>", "Show detailed information about a specific dataset"),
                    ("dataset export <id>", "Show available export formats for a dataset")
                ]
                for cmd, desc in ods_commands:
                    output.append(f"  {cmd:<25}", style=Style(color="cyan", bold=True))
                    output.append(f": {desc}\n", style=Style(color="white"))

            elif isinstance(self.explorer, FrenchGouvCatExplorer):
                output.append("French Government Commands:\n", style=Style(color="yellow", bold=True))
                fr_commands = [
                    ("list datasets", "Show all available datasets"),
                    ("dataset meta <id>", "Show metadata for a specific dataset"),
                    ("resource meta <dataset_id> <resource_id>", "Show metadata for a specific resource"),
                    ("list orgs", "Show all organizations in the catalog")
                ]
                for cmd, desc in fr_commands:
                    output.append(f"  {cmd:<25}", style=Style(color="cyan", bold=True))
                    output.append(f": {desc}\n", style=Style(color="white"))

            # Add examples section if connected
            output.append("\nExample Usage:\n", style=Style(color="green", bold=True))
            output.append("--------------\n")
            if isinstance(self.explorer, CkanCatExplorer):
                output.append("  search police 10", style=Style(color="cyan"))
                output.append("     : Search for 'police' datasets, limit to 10 results\n", style=Style(color="white"))
                output.append("  package info london-crime", style=Style(color="cyan"))
                output.append("     : Show details for package named 'london-crime'\n", style=Style(color="white"))
            elif isinstance(self.explorer, OpenDataSoftCatExplorer):
                output.append("  dataset info power-consumption", style=Style(color="cyan"))
                output.append("     : Show details for dataset 'power-consumption'\n", style=Style(color="white"))
                output.append("  export options energy-data", style=Style(color="cyan"))
                output.append("     : Show export formats for 'energy-data'\n", style=Style(color="white"))
            elif isinstance(self.explorer, FrenchGouvCatExplorer):
                output.append("  dataset meta 123abc", style=Style(color="cyan"))
                output.append("     : Show metadata for dataset with ID '123abc'\n", style=Style(color="white"))
                output.append("  resource meta 123abc res456", style=Style(color="cyan"))
                output.append("     : Show metadata for resource 'res456' in dataset '123abc'\n", style=Style(color="white"))
        else:
            # If not connected, show connection example
            output.append("\nConnect First:\n", style=Style(color="yellow", bold=True))
            output.append("Use 'show catalogs' to see available catalogs, then connect to one:\n", style=Style(color="white"))
            output.append("  connect london", style=Style(color="cyan"))
            output.append("     : Connect to the London Data Store\n", style=Style(color="white"))

        return output

    def clear_log(self):
        """Clear the log display."""
        if self.logger_handler:
            self.logger_handler.clear()

    def load_ckan_dataset(self, dataset_id):
        """Load a CKAN dataset into a Polars DataFrame"""
        if not isinstance(self.explorer, CkanCatExplorer):
            return "Not connected to a CKAN explorer. Use connect() first."
        if not isinstance(self.loader, CkanCatResourceLoader):
            return "Not connected to a CKAN catalog"
        try:
            dataset = self.explorer.show_package_info(dataset_id)
            if not dataset:
                raise ValueError(f"No dataset found with ID: {dataset_id}")
            resource_data = self.explorer.extract_resource_url(dataset)
            if not resource_data:
                raise ValueError(f"No downloadable resources found for dataset: {dataset_id}")
            return self.loader.polars_data_loader(resource_data)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise e

    def load_opendatasoft_dataset(self, dataset_id, format_type, api_key=None):
        """Load an OpenDataSoft dataset into a Polars DataFrame"""
        if not isinstance(self.explorer, OpenDataSoftCatExplorer):
            return "Not connected to a CKAN explorer. Use connect() first."
        if not isinstance(self.loader, OpenDataSoftResourceLoader):
            return "Not connected to an OpenDataSoft catalog"
        try:
            resource_data = self.explorer.show_dataset_export_options(dataset_id)
            if not resource_data:
                raise ValueError(f"No dataset found with ID: {dataset_id}")
            return self.loader.polars_data_loader(resource_data, format_type, api_key=api_key)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise e

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        rich_log = self.query_one(RichLog)
        if event.button.id == "show-catalogs":
            self.clear_log()
            rich_log.write(self.format_catalog_list())
        elif event.button.id == "show-commands":
            self.clear_log()
            rich_log.write(self.format_commands_list())

    async def on_input_submitted(self, message: Input.Submitted):
        """Handle input commands."""
        # Split and clean input
        cmd = message.value.strip().split()
        if not cmd:
            return

        command = cmd[0].lower()
        self.clear_log()
        rich_log = self.query_one(RichLog)

        match command:
            case "connect":
                if len(cmd) < 2:
                    rich_log.write(Text("Please specify a catalog to connect to\n", style=Style(color="yellow")))
                    rich_log.write(self.format_catalog_list())
                    return

                catalog = cmd[1].lower()
                if catalog not in self.catalogs:
                    rich_log.write(Text(f"Invalid catalog: {catalog}\n", style=Style(color="red")))
                    rich_log.write(self.format_catalog_list())
                    return

                try:
                    catalog_type, catalog_enum = self.catalogs[catalog]
                    self.session = CatSession(catalog_enum)
                    self.session.start_session()
                    self.explorer, self.loader = self.create_explorer()

                    if self.active_catalog_button:
                        self.active_catalog_button.remove()

                    button_container = self.query_one("#button-container")
                    self.active_catalog_button = Button(f"Connected: {catalog.upper()}", classes="active-catalog")
                    button_container.mount(self.active_catalog_button)

                    catalog_type_name = self.session.get_catalogue_type().value
                    rich_log.write(Text(f"Connected to {catalog} ({catalog_type_name})\n", style=Style(color="green")))
                    rich_log.write(Text(f"URL: {catalog_enum.value}\n", style=Style(color="blue")))

                    # Check site health after connection
                    await self._check_site_health()
                except Exception as e:
                    rich_log.write(Text(f"Error connecting to {catalog}: {str(e)}\n", style=Style(color="red")))

            case "close":
                if self.session:
                    # Get catalog info before closing - safely extract name from button text
                    if self.active_catalog_button:
                        catalog_name = self.active_catalog_button.label.split(":")[-1]
                    else:
                        catalog_name = "UNKNOWN"

                    catalog_type = self.session.get_catalogue_type().value

                    # Close connection and cleanup
                    self.session.close_session()
                    self.session = None
                    self.explorer = None

                    # Remove button
                    if self.active_catalog_button:
                        self.active_catalog_button.remove()
                        self.active_catalog_button = None

                    # Show informative close message
                    rich_log.write(Text(f"Connection Closed: {catalog_name} ({catalog_type})\n",
                                    style=Style(color="green")))
                else:
                    rich_log.write(Text("No active connection\n", style=Style(color="yellow")))

            case "list":
                if not self.explorer:
                    rich_log.write(Text("No active connection. Please connect to a catalog first.\n", style=Style(color="yellow")))
                    return

                if len(cmd) < 2:
                    rich_log.write(Text("Please specify what to list (packages, datasets, orgs)\n", style=Style(color="yellow")))
                    return

                subcommand = cmd[1].lower()
                try:
                    match self.explorer:
                        case CkanCatExplorer():
                            match subcommand:
                                case "packages":
                                    packages = self.explorer.get_package_list()
                                    rich_log.write(Text(f"Found {len(packages)} packages\n\n", style=Style(color="green", bold=True)))
                                    rich_log.write(packages)
                                case "orgs":
                                    count, orgs = self.explorer.get_organisation_list()
                                    rich_log.write(Text(f"Found {count} organizations\n\n", style=Style(color="green", bold=True)))
                                    rich_log.write(orgs)
                                case _:
                                    rich_log.write(Text(f"Unknown list command: {subcommand}\n", style=Style(color="yellow")))
                        case OpenDataSoftCatExplorer():
                            match subcommand:
                                case "datasets":
                                    datasets = self.explorer.fetch_all_datasets()
                                    if datasets:
                                        rich_log.write(Text(f"Found {len(datasets)} datasets\n\n", style=Style(color="green", bold=True)))
                                        rich_log.write(datasets)
                                    else:
                                        rich_log.write(Text("No datasets found\n", style=Style(color="yellow")))
                                case _:
                                    rich_log.write(Text(f"Unknown list command: {subcommand}\n", style=Style(color="yellow")))
                        case FrenchGouvCatExplorer():
                            match subcommand:
                                case "datasets":
                                    datasets = self.explorer.get_all_datasets()
                                    if datasets:
                                        rich_log.write(Text(f"Found {len(datasets)} datasets\n\n", style=Style(color="green", bold=True)))
                                        rich_log.write(datasets)
                                    else:
                                        rich_log.write(Text("No datasets found\n", style=Style(color="yellow")))
                                case "orgs":
                                    orgs = self.explorer.get_all_orgs()
                                    if orgs:
                                        rich_log.write(Text(f"Found {len(orgs)} organizations\n\n", style=Style(color="green", bold=True)))
                                        rich_log.write(orgs)
                                    else:
                                        rich_log.write(Text("No organizations found\n", style=Style(color="yellow")))
                                case _:
                                    rich_log.write(Text(f"Unknown list command: {subcommand}\n", style=Style(color="yellow")))
                except Exception as e:
                    rich_log.write(Text(f"Error: {str(e)}\n", style=Style(color="red")))

            case "search" if isinstance(self.explorer, CkanCatExplorer):
                if len(cmd) < 3:
                    rich_log.write(Text("Please provide a search query and number of rows\n", style=Style(color="yellow")))
                    return
                try:
                    num_rows = int(cmd[2])
                    results = self.explorer.package_search_condense(cmd[1], num_rows)
                    if results:
                        rich_log.write(Text(f"Found {len(results)} matches\n\n", style=Style(color="green", bold=True)))
                        rich_log.write(results)
                    else:
                        rich_log.write(Text("No matching packages found\n", style=Style(color="yellow")))
                except ValueError:
                    rich_log.write(Text("Number of rows must be a valid number\n", style=Style(color="red")))
                except Exception as e:
                    rich_log.write(Text(f"Error: {str(e)}\n", style=Style(color="red")))

            case "load":
                if not self.explorer:
                    rich_log.write(Text("No active connection. Please connect to a catalog first.\n", style=Style(color="yellow")))
                    return

                if len(cmd) < 2:
                    rich_log.write(Text("Please provide the dataset ID\n", style=Style(color="yellow")))
                    return

                dataset_id = cmd[1]

                try:
                    match self.explorer:
                        case CkanCatExplorer():
                            df = self.load_ckan_dataset(dataset_id)
                        case OpenDataSoftCatExplorer():
                            format_type = cmd[2] if len(cmd) > 2 else "csv"
                            api_key = cmd[3] if len(cmd) > 3 else None
                            df = self.load_opendatasoft_dataset(dataset_id, format_type, api_key)
                        case _:
                            raise ValueError("Unsupported catalog type")

                    if isinstance(df, str):
                        rich_log.write(Text(df + "\n", style=Style(color="red")))
                    else:
                        rich_log.write(Text("Data Loaded Successfully ✅\n", style=Style(color="green", bold=True)))
                        rich_log.write("DATA COLUMNS AND DATA TYPES")
                        rich_log.write(df.columns)
                        rich_log.write(df.dtypes)
                        rich_log.write("DATA SAMPLE")
                        rich_log.write(df.head(10))
                except Exception as e:
                    rich_log.write(Text(f"Error loading data: {str(e)}\n", style=Style(color="red")))

            case "package" | "dataset" | "resource":
                if not self.explorer:
                    rich_log.write(Text("No active connection. Please connect to a catalog first.\n", style=Style(color="yellow")))
                    return

                if len(cmd) < 3:
                    rich_log.write(Text(f"Please provide the {command} command and ID\n", style=Style(color="yellow")))
                    return

                subcommand = cmd[1].lower()
                identifier = cmd[2]

                try:
                    match self.explorer:
                        case CkanCatExplorer() if command == "package":
                            match subcommand:
                                case "info":
                                    info = self.explorer.show_package_info(identifier)
                                    rich_log.write(info)
                                case _:
                                    rich_log.write(Text(f"Unknown package command: {subcommand}\n", style=Style(color="yellow")))
                        case OpenDataSoftCatExplorer() if command == "dataset":
                            match subcommand:
                                case "info":
                                    info = self.explorer.show_dataset_info(identifier)
                                    rich_log.write(info)
                                case "export":
                                    options = self.explorer.show_dataset_export_options(identifier)
                                    rich_log.write(options)
                                case _:
                                    rich_log.write(Text(f"Unknown dataset command: {subcommand}\n", style=Style(color="yellow")))
                        case FrenchGouvCatExplorer():
                            match command, subcommand:
                                case "dataset", "meta":
                                    meta = self.explorer.get_dataset_meta(identifier)
                                    rich_log.write(meta)
                                case "resource", "meta":
                                    if len(cmd) < 4:
                                        rich_log.write(Text("Please provide both dataset_id and resource_id\n", style=Style(color="yellow")))
                                        return
                                    meta = self.explorer.get_dataset_resource_export(identifier, cmd[3])
                                    rich_log.write(meta)
                                case _:
                                    rich_log.write(Text(f"Unknown {command} command: {subcommand}\n", style=Style(color="yellow")))
                except Exception as e:
                    rich_log.write(Text(f"Error: {str(e)}\n", style=Style(color="red")))

            case "quit":
                if self.session:
                    self.session.close_session()
                self.exit()


if __name__ == "__main__":
    app = InteractiveCats()
    app.run()
