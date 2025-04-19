from textual.widgets import RichLog, DataTable, Input

from herding_cats_interactive.ui.components.catalogue_button import CatalogButton
from herding_cats_interactive.ui.components.command_button import CommandButton


class BindingHandler:
    def __init__(self, app):
        self.app = app
        self.rich_log = app.query_one(RichLog)
        self.data_table = app.query_one(DataTable)
        self.actions = {
            "show_catalogs": lambda: self.app.query_one(
                CatalogButton
            )._format_catalog_list(),
            "show_commands": lambda: self.app.query_one(
                CommandButton
            )._format_commands_list(),
            "focus_log": lambda: self.rich_log.focus(),
            "focus_table": lambda: self.data_table.focus(),
            "focus_input": lambda: self.app.query_one(Input).focus(),
            "unfocus_input": lambda: self.app.query_one(Input).blur(),
            "reset_app": lambda: self.app.reset_app(),
        }

    def handle_action(self, action: str) -> None:
        if action in self.actions:
            if action in ["show_catalogs", "show_commands"]:
                formatted_text = self.actions[action]()
                self.rich_log.clear()
                self.rich_log.focus()
                self.rich_log.write(formatted_text)
            else:
                self.actions[action]()
