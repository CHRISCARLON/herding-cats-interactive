from rich.text import Text
from rich.style import Style
from textual.widgets import RichLog
from typing import Any
from collections import deque
from rich.text import Text
from textual.widgets import RichLog
from typing import Deque, Optional

class ExtendedRichLogHandler:
    def __init__(self, log_display: RichLog):
        self._rich_log = log_display
        self._history: Deque[Text] = deque(maxlen=1000)
        self._current_position: int = -1
        self.styles = {
            "INFO": Style(color="blue"),
            "SUCCESS": Style(color="green"),
            "WARNING": Style(color="yellow"),
            "ERROR": Style(color="red"),
            "DEBUG": Style(color="cyan")
        }

    def write_structured_data(self, data: Any, indent: int = 0) -> Text:
        """
        Recursively format structured data with proper indentation.
        Args:
            data: The data to format
            indent: Current indentation level
        Returns:
            Text: A Rich Text object with colored formatting
        """
        indent_str = " " * indent
        result = Text()

        if isinstance(data, (list, tuple)):
            if not data:  # Handle empty lists
                result.append(f"{indent_str}(empty)\n")
                return result

            # For packages list, handle it as a special case
            if all(isinstance(x, str) for x in data):
                for i, item in enumerate(data, 1):
                    # Format each package name nicely
                    package_name = item.strip('-').replace('-', ' ').title()
                    result.append(f"{indent_str}{i}. {package_name}\n")
                return result

            # For other lists
            for item in data:
                result.append(f"{indent_str}• ")
                result.append(self.write_structured_data(item, indent + 2))
            return result

        elif isinstance(data, dict):
            if not data:  # Handle empty dicts
                result.append(f"{indent_str}(empty dictionary)\n")
                return result

            # Add a header for the dictionary
            result.append(f"{indent_str}Dictionary containing {len(data)} items:\n", 
                        style=Style(color="yellow"))

            # For each key-value pair, format nicely with colors
            for key, value in data.items():
                # Clean up the key name
                clean_key = key.strip('-').replace('-', ' ').title()
                
                # Start the line with indentation
                result.append(f"{indent_str}")
                
                # Add "Key:" label in blue
                result.append("Key: ", style=Style(color="cyan", bold=True))
                # Add the actual key in white
                result.append(f"{clean_key}", style=Style(color="white"))
                
                # Add separator
                result.append(" | ")
                
                # Add "Value:" label in blue
                result.append("Value: ", style=Style(color="cyan", bold=True))
                
                # Handle the value based on its type
                if isinstance(value, (dict, list, tuple)):
                    result.append("\n")
                    result.append(self.write_structured_data(value, indent + 2))
                else:
                    # Add the actual value in green
                    result.append(f"{value}\n", style=Style(color="green"))
                # Create the formatted text
            
            # Write to history and display
            self.write(result)
            return result

        else:
            # Handle basic types
            value = str(data).strip()
            # If it's a package name, clean it up
            if isinstance(data, str) and '-' in value:
                value = value.strip('-').replace('-', ' ').title()
            result.append(f"{indent_str}{value}\n")
            return result

    def write(self, message):
        """Write a message and store in history."""
        if hasattr(message, "record"):
            level = message.record["level"].name
            style = self.styles.get(level, Style())
            text = Text(str(message).strip() + "\n", style=style)
        else:
            text = Text.from_markup(str(message).strip() + "\n") if not isinstance(message, Text) else message

        # Add to history
        self._history.append(text)
        self._current_position = len(self._history) - 1
        
        # Write to RichLog
        self._rich_log.write(text)

    def show_previous(self) -> Optional[Text]:
        """Show previous entry in history."""
        if self._current_position > 0:
            self._current_position -= 1
            self._rich_log.clear()
            for i in range(self._current_position + 1):
                self._rich_log.write(self._history[i])
            return self._history[self._current_position]
        return None
    
    def show_next(self) -> Optional[Text]:
        """Show next entry in history."""
        if self._current_position < len(self._history) - 1:
            self._current_position += 1
            self._rich_log.clear()
            for i in range(self._current_position + 1):
                self._rich_log.write(self._history[i])
            return self._history[self._current_position]
        return None

    def clear(self):
        """Clear both history and display."""
        self._history.clear()
        self._current_position = -1
        self._rich_log.clear()

    def flush(self):
        """Required for handler interface."""
        pass