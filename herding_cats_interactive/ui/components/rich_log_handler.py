from rich.text import Text
from rich.style import Style
from textual.widgets import RichLog

class TextualRichLogHandler:
    """Log handler that sends output to a Textual RichLog widget."""
    
    def __init__(self, log_display: RichLog):
        self.log_display = log_display
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