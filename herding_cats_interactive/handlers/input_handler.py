import asyncio
import os

from textual.widgets import RichLog, Input
from rich.text import Text
from rich.style import Style

from HerdingCats.explorer.explore import (
    CkanCatExplorer,
    OpenDataSoftCatExplorer,
    FrenchGouvCatExplorer,
)
from HerdingCats.loader.loader import CkanLoader, OpenDataSoftLoader, FrenchGouvLoader


class InputHandler:
    """
    Input Handler
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
            "quit": self._handle_quit,
            "list": self._handle_list,
            "package": self._handle_info,
            "dataset": self._handle_info,
            "resource": self._handle_info,
            "load": self._handle_load,
            "search": self._handle_search,
        }

        handler = command_handlers.get(command)
        if handler:
            await handler(cmd)
        else:
            # Handle unknown command
            self.rich_log.write(Text("❌ Unknown command\n", style=Style(color="red")))
            self.rich_log.write(
                Text("Available commands:\n", style=Style(color="yellow"))
            )
            self.rich_log.write(self.app.format_commands_list())

    async def compose_loading_dots(self, command: str) -> None:
        """Display loading dots animation."""
        dots = ["   ", ".  ", ".. ", "..."]
        for dot in dots:
            text = Text()
            text.append(
                "⚡ Please Wait! Processing Command: ",
                style=Style(color="cyan", italic=True),
            )
            text.append(command, style=Style(color="white"))
            text.append(dot + "\n", style=Style(color="cyan"))
            self.app.clear_log()
            self.rich_log.write(text)
            await asyncio.sleep(0.1)

    def load_ckan_dataset(self, dataset_id, format_type):
        """Load a CKAN dataset into a Polars DataFrame"""
        if not isinstance(self.app.explorer, CkanCatExplorer):
            return "Not connected to a CKAN explorer. Use connect() first."
        if not isinstance(self.app.loader, CkanLoader):
            return "Not connected to a CKAN catalog"
        try:
            dataset = self.app.explorer.show_package_info(dataset_id)
            if not dataset:
                raise ValueError(f"No dataset found with ID: {dataset_id}")
            resource_data = self.app.explorer.extract_resource_url(dataset)
            if not resource_data:
                raise ValueError(
                    f"No downloadable resources found for dataset: {dataset_id}"
                )
            return self.app.loader.polars_data_loader(resource_data, format_type)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise e

    def load_opendatasoft_dataset(self, dataset_id, format_type, api_key=None):
        """Load an OpenDataSoft dataset into a Polars DataFrame"""
        if not isinstance(self.app.explorer, OpenDataSoftCatExplorer):
            return "Not connected to a OpenDataSoft explorer. Use connect() first."
        if not isinstance(self.app.loader, OpenDataSoftLoader):
            return "Not connected to an OpenDataSoft catalog"

        if api_key is None:
            api_key = os.getenv("OPENDATASOFT_API_KEY")

        try:
            resource_data = self.app.explorer.show_dataset_export_options(dataset_id)
            if not resource_data:
                raise ValueError(f"No dataset found with ID: {dataset_id}")
            return self.app.loader.polars_data_loader(
                resource_data, format_type, api_key=api_key
            )
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise e

    def load_french_gouv_dataset(self, dataset_id, format_type):
        """Load an French Government dataset into a Polars DataFrame"""
        if not isinstance(self.app.explorer, FrenchGouvCatExplorer):
            return "Not connected to French Government explorer. Use connect() first."
        if not isinstance(self.app.loader, FrenchGouvLoader):
            return "Not connected to French Government catalog"

        try:
            resource_data = self.app.explorer.get_dataset_meta(dataset_id)
            data_to_load = self.app.explorer.get_dataset_resource_meta(resource_data)
            if not data_to_load:
                raise ValueError(f"No dataset found with ID: {dataset_id}")
            return self.app.loader.polars_data_loader(
                data_to_load, format_type, api_key=None
            )
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            raise e

    async def _handle_connect(self, cmd: list) -> None:
        """Handle the connect command."""
        if len(cmd) < 2:
            self.rich_log.write(
                Text("Please Specify a Catalog\n", style=Style(color="yellow"))
            )
            self.rich_log.write(self.app.format_catalog_list())
            return

        catalog = cmd[1].lower()
        success, error, catalog_enum = await self.app.connect_to_catalog(catalog)

        if not success:
            self.rich_log.write(
                Text(f"Invalid Catalog: {catalog}\n", style=Style(color="red"))
            )
            self.rich_log.write(self.app.format_catalog_list())
            return

        # Update UI after successful connection
        self.app.update_catalog_button(catalog)

        catalog_type_name = self.app.session.catalogue_type
        self.rich_log.write(
            Text(
                f"Connected to {catalog} ({catalog_type_name})\n",
                style=Style(color="green"),
            )
        )
        self.rich_log.write(
            Text(f"URL: {catalog_enum.value}\n", style=Style(color="blue"))
        )
        self.input.value = ""
        self.app.set_timer(3, self.app.clear_log)

    async def _handle_close(self, cmd: list) -> None:
        """Handle the close command."""

        if not self.app.session:
            self.rich_log.write(
                Text("No Active Connection...\n", style=Style(color="yellow"))
            )
            self.input.value = ""
            self.rich_log.write(
                Text("Please Specify a Catalog\n", style=Style(color="yellow"))
            )
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

        if self.app.data_table:
            self.app.data_table.clear(columns=True)

        # Show close message
        self.rich_log.write(
            Text(
                f"Connection Closed: {message} ({catalog_type})\n",
                style=Style(color="green"),
            )
        )
        self.input.value = ""
        self.app.set_timer(1, self.app.clear_log)

    async def _handle_quit(self, cmd: list) -> None:
        """Handle the quit command."""
        if self.app.session:
            self.app.session.close_session()
        self.app.exit()

    async def _handle_list(self, cmd: list) -> None:
        """Handle the list command for different catalog types."""
        if not self.app.explorer:
            self.rich_log.write(
                Text(
                    "No active connection. Please connect to a catalog first.\n",
                    style=Style(color="yellow"),
                )
            )
            return

        if len(cmd) < 2:
            self.rich_log.write(
                Text(
                    "Please specify what to list (packages, datasets, orgs)\n",
                    style=Style(color="yellow"),
                )
            )
            return

        subcommand = cmd[1].lower()
        try:
            match self.app.explorer:
                case CkanCatExplorer():
                    match subcommand:
                        case "packages":
                            packages = self.app.explorer.get_package_list()
                            self.rich_log.write(
                                Text(
                                    f"Found {len(packages)} packages\n\n",
                                    style=Style(color="green", bold=True),
                                )
                            )
                            self.app.logger_handler.write_and_display_structured_data(
                                packages
                            )
                        case "orgs":
                            count, orgs = self.app.explorer.get_organisation_list()
                            self.rich_log.write(
                                Text(
                                    f"Found {count} organizations\n\n",
                                    style=Style(color="green", bold=True),
                                )
                            )
                            self.app.logger_handler.write_and_display_structured_data(
                                orgs
                            )
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown list command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

                case OpenDataSoftCatExplorer():
                    match subcommand:
                        case "datasets":
                            datasets = self.app.explorer.fetch_all_datasets()
                            if datasets:
                                self.rich_log.write(
                                    Text(
                                        f"Found {len(datasets)} datasets\n\n",
                                        style=Style(color="green", bold=True),
                                    )
                                )
                                self.app.logger_handler.write_and_display_structured_data(
                                    datasets
                                )
                            else:
                                self.rich_log.write(
                                    Text(
                                        "No datasets found\n",
                                        style=Style(color="yellow"),
                                    )
                                )
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown list command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

                case FrenchGouvCatExplorer():
                    match subcommand:
                        case "datasets":
                            datasets = self.app.explorer.get_all_datasets()
                            if datasets:
                                self.rich_log.write(
                                    Text(
                                        f"Found {len(datasets)} datasets\n\n",
                                        style=Style(color="green", bold=True),
                                    )
                                )
                                datasets_formatted = (
                                    self.app.logger_handler.write_structured_data(
                                        datasets
                                    )
                                )
                                self.rich_log.write(datasets_formatted)
                            else:
                                self.rich_log.write(
                                    Text(
                                        "No datasets found\n",
                                        style=Style(color="yellow"),
                                    )
                                )
                        case "orgs":
                            orgs = self.app.explorer.get_all_organisations()
                            if orgs:
                                self.rich_log.write(
                                    Text(
                                        f"Found {len(orgs)} organizations\n\n",
                                        style=Style(color="green", bold=True),
                                    )
                                )
                                orgs_formatted = (
                                    self.app.logger_handler.write_structured_data(orgs)
                                )
                                self.rich_log.write(orgs_formatted)
                            else:
                                self.rich_log.write(
                                    Text(
                                        "No organizations found\n",
                                        style=Style(color="yellow"),
                                    )
                                )
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown list command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

        except Exception as e:
            self.rich_log.write(Text(f"Error: {str(e)}\n", style=Style(color="red")))

    async def _handle_info(self, cmd: list) -> None:
        """Handle info commands for different catalog types."""
        if not self.app.explorer:
            self.rich_log.write(
                Text(
                    "No active connection. Please connect to a catalog first.\n",
                    style=Style(color="yellow"),
                )
            )
            return

        if len(cmd) < 3:
            self.rich_log.write(
                Text(
                    "Please provide both command type (package/dataset/resource) and ID\n",
                    style=Style(color="yellow"),
                )
            )
            return

        command = cmd[0].lower()
        subcommand = cmd[1].lower()
        identifier = cmd[2]

        try:
            match self.app.explorer:
                case CkanCatExplorer() if command == "package":
                    match subcommand:
                        case "info":
                            info = self.app.explorer.show_package_info(identifier)
                            info_formatted = (
                                self.app.logger_handler.write_structured_data(info)
                            )
                            self.rich_log.write(info_formatted)
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown package command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

                case OpenDataSoftCatExplorer() if command == "dataset":
                    match subcommand:
                        case "info":
                            info = self.app.explorer.show_dataset_info(identifier)
                            info_formatted = (
                                self.app.logger_handler.write_structured_data(info)
                            )
                            self.rich_log.write(info_formatted)
                        case "export":
                            options = self.app.explorer.show_dataset_export_options(
                                identifier
                            )
                            options_formatted = (
                                self.app.logger_handler.write_structured_data(options)
                            )
                            self.rich_log.write(options_formatted)
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown dataset command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

                case FrenchGouvCatExplorer():
                    match command, subcommand:
                        case "dataset", "meta":
                            meta = self.app.explorer.get_dataset_meta(identifier)
                            meta_formatted = (
                                self.app.logger_handler.write_structured_data(meta)
                            )
                            self.rich_log.write(meta_formatted)
                        case "resource", "meta":
                            input_meta = self.app.explorer.get_dataset_meta(identifier)
                            meta = self.app.explorer.get_dataset_resource_meta(
                                input_meta
                            )
                            meta_formatted = (
                                self.app.logger_handler.write_structured_data(meta)
                            )
                            self.rich_log.write(meta_formatted)
                        case _:
                            self.rich_log.write(
                                Text(
                                    f"Unknown {command} command: {subcommand}\n",
                                    style=Style(color="yellow"),
                                )
                            )

                case _:
                    self.rich_log.write(
                        Text(
                            f"Current explorer doesn't support {command} info commands\n",
                            style=Style(color="yellow"),
                        )
                    )

        except Exception as e:
            self.rich_log.write(Text(f"Error: {str(e)}\n", style=Style(color="red")))

    async def _handle_load(self, cmd: list) -> None:
        """Handle the load command for different catalog types."""
        if not self.app.explorer:
            self.rich_log.write(
                Text(
                    "No active connection. Please connect to a catalog first.\n",
                    style=Style(color="yellow"),
                )
            )
            return

        if len(cmd) < 2:
            self.rich_log.write(
                Text("Please provide the dataset ID\n", style=Style(color="yellow"))
            )
            return

        dataset_id = cmd[1]

        try:
            # Load data based on explorer type
            df = None
            match self.app.explorer:
                case CkanCatExplorer():
                    format_type = cmd[2] if len(cmd) > 2 else None
                    df = self.load_ckan_dataset(dataset_id, format_type)
                case OpenDataSoftCatExplorer():
                    format_type = cmd[2] if len(cmd) > 2 else "csv"
                    api_key = cmd[3] if len(cmd) > 3 else None
                    df = self.load_opendatasoft_dataset(
                        dataset_id, format_type, api_key
                    )
                case FrenchGouvCatExplorer():
                    format_type = cmd[2] if len(cmd) > 2 else "csv"
                    df = self.load_french_gouv_dataset(dataset_id, format_type)
                case _:
                    raise ValueError("Unsupported catalog type")

            if isinstance(df, str):
                # Handle error message
                self.rich_log.write(Text(df + "\n", style=Style(color="red")))
                return

            # Display success message and metadata in RichLog
            self.rich_log.write(
                Text(
                    "Data Loaded Successfully ✅\n",
                    style=Style(color="green", bold=True),
                )
            )
            self.rich_log.write(
                Text(
                    "\nDATA COLUMNS AND DATA TYPES\n",
                    style=Style(color="cyan", bold=True),
                )
            )

            # Format column info
            for col, dtype in zip(df.columns, df.dtypes):
                self.rich_log.write(
                    Text(f"{col}: {dtype}\n", style=Style(color="white"))
                )

            # Update DataTable
            # Clear existing data
            self.app.data_table.clear()

            # Add columns
            self.app.data_table.add_columns(*[str(col) for col in df.columns])

            # Add rows - using Polars row iteration
            for row in df.head(100).iter_rows():
                self.app.data_table.add_row(*[str(val) for val in row])

            # Focus the data table
            self.app.data_table.focus()

        except Exception as e:
            self.rich_log.write(
                Text(f"Error loading data: {str(e)}\n", style=Style(color="red"))
            )

    async def _handle_search(self, cmd: list) -> None:
        """Handle search commands for different catalog types."""
        if not self.app.explorer:
            self.rich_log.write(
                Text(
                    "No active connection. Please connect to a catalog first.\n",
                    style=Style(color="yellow"),
                )
            )
            return

        if len(cmd) < 2:
            self.rich_log.write(
                Text("Please provide a search query\n", style=Style(color="yellow"))
            )
            return

        query = cmd[1]
        num_rows = (
            int(cmd[2]) if len(cmd) > 2 else 10
        )  # Default to 10 results if not specified

        try:
            match self.app.explorer:
                case CkanCatExplorer():
                    results = self.app.explorer.package_search_condense(query, num_rows)
                    if results:
                        self.rich_log.write(
                            Text(
                                f"Found matches for: '{query}'\n\n",
                                style=Style(color="green", bold=True),
                            )
                        )
                        results_formatted = (
                            self.app.logger_handler.write_structured_data(results)
                        )
                        self.rich_log.write(results_formatted)
                    else:
                        self.rich_log.write(
                            Text(
                                "No matching packages found\n",
                                style=Style(color="yellow"),
                            )
                        )
                case _:
                    self.rich_log.write(
                        Text(
                            "Search not supported for this catalog type\n",
                            style=Style(color="yellow"),
                        )
                    )
        except ValueError as ve:
            self.rich_log.write(
                Text(f"Invalid input: {str(ve)}\n", style=Style(color="red"))
            )
        except Exception as e:
            self.rich_log.write(
                Text(f"Error during search: {str(e)}\n", style=Style(color="red"))
            )
