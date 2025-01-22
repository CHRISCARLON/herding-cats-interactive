# HerdingCats Interactive 🐈‍⬛

<img width="1501" alt="Screenshot 2025-01-22 at 20 02 48" src="https://github.com/user-attachments/assets/b500fe10-1942-4ffa-9086-f488cbe4f834" />

## Getting Started

After launching the application, you'll see a welcome message along with several interactive options.

Here's how you can begin using the InteractiveCats application:

### Basic Commands

- **Connect to a Catalog**:
  - Use `connect <catalog_name>` to connect to your desired data catalog.
  - Example: `connect london-datastore`

- **Close the Current Connection**:
  - Type `close` to disconnect from the an actively connected catalog.

- **Quit the Application**:
  - Enter `quit` or press 'q' to exit the application anytime.

### Using the UI Buttons

- **Show Available Catalogs**: Click this button to view a list of all available data catalogs you can connect to.
- **Show Commands**: Click this button to view a list of commands you can use within the application.

## Exploring Connected Catalogs

Once you've connected to a catalog, you can perform different actions depending on the type of catalog:

### If You Are Connected to a CKAN Catalog:
- **List Packages**:
  - Use `list packages` to see all available datasets.
- **Package Information**:
  - Use `package info <package_name>` to get detailed information on a dataset.
- **Search Datasets**:
  - Use `search <query> <rows>` to find datasets related to your query and limit the results.
- **List Organisations**:
  - Use `list orgs` to see all organizations in the catalog.

### If You Are Connected to an OpenDataSoft Catalog:
- **List Datasets**:
  - Use `list datasets` to see all datasets in the catalog.
- **Dataset Information**:
  - Use `dataset info <dataset_id>` to view detailed dataset information.
- **Dataset Export Options**:
  - Use `dataset export <dataset_id>` to view available export formats for a dataset.

### If You Are Connected to the French Government Catalog:
- **List Datasets**:
  - Use `list datasets` to view all available datasets.
- **Dataset Metadata**:
  - Use `dataset meta <dataset_id>` to show metadata for a given dataset.
- **Resource Metadata**:
  - Use `resource meta <dataset_id>` to show metadata for a given resource.

## Additional Features

- **Loading Data**: (does not work for French Gov Cat yet 🐈)
  - Use `load <dataset_id> [format] [api-key]` to load a dataset and examine its structure and sample data. For OpenDataSoft, specify a format and optionally an API key.
- **Rich Logging**: The application logs each interaction in a rich-text format for easy readability.

## Need Help?

At any time, you can use the `Show Commands` button to review available commands and see example usages.
