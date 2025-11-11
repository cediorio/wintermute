"""Status pane widget for displaying connection and memory status."""

from typing import Optional

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class StatusPane(Widget):
    """Widget displaying connection status and memory statistics."""

    # Reactive properties that trigger re-render when changed
    ollama_connected: reactive[bool] = reactive(False)
    memory_connected: reactive[bool] = reactive(False)
    memory_count: reactive[int] = reactive(0)
    model_name: reactive[str] = reactive("Unknown")

    def update_status(
        self,
        ollama_connected: Optional[bool] = None,
        memory_connected: Optional[bool] = None,
        memory_count: Optional[int] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Update the status display.

        Args:
            ollama_connected: Whether Ollama is connected.
            memory_connected: Whether OpenMemory is connected.
            memory_count: Number of memories stored.
            model_name: Name of the active model.
        """
        if ollama_connected is not None:
            self.ollama_connected = ollama_connected
        if memory_connected is not None:
            self.memory_connected = memory_connected
        if memory_count is not None:
            self.memory_count = memory_count
        if model_name is not None:
            self.model_name = model_name

    def render(self) -> Text:
        """
        Render the status display.

        Returns:
            Rich Text object with formatted status information.
        """
        text = Text()

        # Title
        text.append("Status\n", style="bold underline")
        text.append("\n")

        # Ollama connection status
        if self.ollama_connected:
            text.append("● ", style="bold green")
            text.append("Ollama: Connected\n")
        else:
            text.append("● ", style="bold red")
            text.append("Ollama: Disconnected\n")

        # Model name
        text.append(f"  Model: {self.model_name}\n", style="dim")
        text.append("\n")

        # OpenMemory connection status
        if self.memory_connected:
            text.append("● ", style="bold green")
            text.append("Memory: Connected\n")
        else:
            text.append("● ", style="bold red")
            text.append("Memory: Disconnected\n")

        # Memory count
        text.append(f"  Memories: {self.memory_count}\n", style="dim")

        return text
