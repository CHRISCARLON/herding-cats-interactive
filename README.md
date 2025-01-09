# Interactive Terminal Session for HerdingCats 🐈‍⬛

## Getting Started

After launching the application, you'll see a welcome message and a couple of interactive options. Here's how you can begin using InteractiveCats:

![image](https://github.com/user-attachments/assets/56519577-8129-4d31-b13b-fac4921b938e)

### Basic Commands

- **Connect to a Catalog**:
  - Use `connect <catalog_name>` to connect to your desired data catalog.
  - Example: `connect london`

- **Close the Current Connection**:
  - Type `close` to disconnect from the current catalog.

- **Quit the Application**:
  - Enter `quit` to exit the application anytime.

### Using the UI Buttons

- **Show Available Catalogs**: Click on this button to view a list of all available data catalogs you can connect to.

- **Show Commands**: Click this button to view a list of commands you can use within the application.

## Exploring Connected Catalogs

Once you've connected to a catalog, you can perform the following actions:

### If You Are Connected to a CKAN Catalog:
- **List Packages**:
  - Use the command `list packages` to see all available datasets.

- **Package Information**:
  - Use `package info <package_name>` to get detailed information about a dataset.

- **Search Datasets**:
  - Use `search <query> <rows>` to find datasets related to your query and limit the results.

### If You Are Connected to an OpenDataSoft Catalog:
- **List Datasets**:
  - Use `list datasets` to see all datasets in the catalog.

- **Dataset Information**:
  - Use `dataset info <dataset_id>` to view detailed dataset information.

### If You Are Connected to the French Government Catalog:
- **List Datasets**:
  - Use `list datasets` to see all datasets available.

- **Dataset Metadata**:
  - Use `dataset meta <dataset_id>` to show metadata for a given dataset.

## Additional Features

- **Loading Data**: Use `load <dataset_id>` to load a dataset and examine its structure and sample data.

- **Rich Logging**: The application logs each interaction in a rich-text format for easy readability.

## Need Help?

At any time, you can use the `Show Commands` button to review available commands and see example usages.
