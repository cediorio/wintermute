"""Chat pane widget for displaying conversation history and input."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input, Static

from wintermute.models.message import Message, MessageRole


class ChatPane(VerticalScroll):
    """Widget for displaying chat messages and handling user input."""

    # Reactive properties
    is_typing: reactive[bool] = reactive(False)
    input_enabled: reactive[bool] = reactive(True)

    def __init__(self, **kwargs):
        """
        Initialize the ChatPane.

        Args:
            **kwargs: Additional keyword arguments for Widget.
        """
        super().__init__(**kwargs)
        self.messages: list[Message] = []
        self._chunk_count = 0  # Track chunks for throttled updates

    def compose(self) -> ComposeResult:
        """Compose the chat pane with message display and input."""
        yield Static(id="message-container")
        yield Input(placeholder="Type a message...", id="chat-input")

    def add_message(self, message: Message) -> None:
        """
        Add a message to the chat history.

        Args:
            message: The Message object to add.
        """
        self.messages.append(message)
        self._update_display()

    def update_last_message(self, content: str, force: bool = False) -> None:
        """
        Update the content of the last message (for streaming).

        Args:
            content: The new content for the last message.
            force: Force update even if throttling would skip it.
        """
        if self.messages:
            self.messages[-1].content = content
            self._chunk_count += 1

            # Update display every 3 chunks or on force (reduces flicker)
            if force or self._chunk_count % 3 == 0:
                self._update_display()
                self.scroll_end(animate=False)

    def _update_display(self) -> None:
        """Update the message display."""
        try:
            container = self.query_one("#message-container", Static)
            container.update(self._render_messages())
        except Exception:
            pass

    def clear_messages(self) -> None:
        """Clear all messages from the chat history."""
        self.messages = []
        self.refresh()

    def get_all_messages(self) -> list[Message]:
        """
        Get all messages in the chat history.

        Returns:
            List of all Message objects.
        """
        return self.messages

    def get_message_count(self) -> int:
        """
        Get the number of messages in chat history.

        Returns:
            Number of messages.
        """
        return len(self.messages)

    def get_current_input(self) -> str:
        """
        Get the current input text.

        Returns:
            Current input string.
        """
        try:
            input_widget = self.query_one("#chat-input", Input)
            return input_widget.value
        except Exception:
            return ""

    def clear_input(self) -> None:
        """Clear the input field."""
        try:
            input_widget = self.query_one("#chat-input", Input)
            input_widget.value = ""
        except Exception:
            pass

    def set_input_enabled(self, enabled: bool) -> None:
        """
        Enable or disable input.

        Args:
            enabled: Whether input should be enabled.
        """
        self.input_enabled = enabled
        try:
            input_widget = self.query_one("#chat-input", Input)
            input_widget.disabled = not enabled
        except Exception:
            pass

    def show_typing_indicator(self) -> None:
        """Show the typing indicator."""
        self.is_typing = True

    def hide_typing_indicator(self) -> None:
        """Hide the typing indicator."""
        self.is_typing = False

    def _format_message(self, message: Message) -> Text:
        """
        Format a message for display.

        Args:
            message: The Message to format.

        Returns:
            Formatted Rich Text object.
        """
        text = Text()

        # Get sender name and style based on role
        if message.role == MessageRole.USER:
            sender = "User"
            sender_style = "cyan bold"
        elif message.role == MessageRole.ASSISTANT:
            sender = message.metadata.get("persona_name", "Assistant")
            sender_style = "green bold"
        else:
            sender = "System"
            sender_style = "yellow bold"

        # Format timestamp
        time_str = message.timestamp.strftime("%H:%M")

        # Build the formatted message
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"{sender}: ", style=sender_style)
        text.append(message.content)

        return text

    def _render_messages(self) -> Text:
        """
        Render messages for display.

        Returns:
            Rich Text object with formatted messages.
        """
        text = Text()

        # Display messages
        if not self.messages:
            text.append("No messages yet. Start a conversation!\n", style="dim italic")
        else:
            for message in self.messages:
                formatted = self._format_message(message)
                text.append(formatted)
                text.append("\n\n")  # Add spacing between messages

        # Show typing indicator if active
        if self.is_typing:
            text.append("Assistant is typing...\n", style="dim italic")

        return text

    def render(self) -> Text:
        """
        Render the chat display (for compatibility with old tests).

        Returns:
            Rich Text object with formatted chat history.
        """
        return self._render_messages()
