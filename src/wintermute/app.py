"""Main Wintermute TUI application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header

from textual.widgets import Input

from wintermute.models.message import Message, MessageRole
from wintermute.services.memory_client import MemoryClient
from wintermute.services.message_handler import MessageHandler
from wintermute.services.ollama_client import OllamaClient
from wintermute.services.character_manager import CharacterManager
from wintermute.ui.chat_pane import ChatPane
from wintermute.ui.character_pane import CharacterPane
from wintermute.ui.status_pane import StatusPane
from wintermute.utils.config import Config


class WintermuteApp(App):
    """Wintermute - TUI chatbot with personality and memory."""

    TITLE = "Wintermute"
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 3fr 1fr;
    }
    
    #chat-container {
        column-span: 1;
        height: 100%;
    }
    
    #right-container {
        column-span: 1;
        height: 100%;
    }
    
    #character-pane {
        height: 60%;
    }
    
    #status-pane {
        height: 40%;
    }
    
    ChatPane {
        border: solid green;
        padding: 1;
    }
    
    CharacterPane {
        border: solid cyan;
        padding: 1;
    }
    
    StatusPane {
        border: solid yellow;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+p", "next_character", "Next Character"),
        Binding("ctrl+n", "previous_character", "Previous Character"),
    ]

    def __init__(self):
        """Initialize the Wintermute application."""
        super().__init__()

        # Load configuration
        self.config = Config()

        # Initialize services
        self.ollama_client = OllamaClient(self.config)
        self.memory_client = MemoryClient(self.config)

        # Initialize character manager
        characters_dir = Path(__file__).parent.parent.parent / "characters"
        self.character_manager = CharacterManager(characters_dir)

        # Initialize message handler
        self.message_handler = MessageHandler(
            self.ollama_client,
            self.memory_client,
        )

    def compose(self) -> ComposeResult:
        """
        Compose the application layout.

        Returns:
            Generator of widgets to compose the app.
        """
        # Header and footer
        yield Header()
        yield Footer()

        # Main content area
        with Container(id="chat-container"):
            yield ChatPane()

        with Vertical(id="right-container"):
            yield CharacterPane(self.character_manager.get_all_characters(), id="character-pane")
            yield StatusPane(id="status-pane")

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Check service connections
        await self._check_connections()

        # Set initial focus to chat input
        chat_pane = self.query_one(ChatPane)
        chat_pane.focus_input()

    async def _check_connections(self) -> None:
        """Check connections to Ollama and OpenMemory."""
        ollama_connected = await self.ollama_client.check_connection()
        memory_connected = await self.memory_client.check_connection()

        # Get memory stats
        stats = await self.memory_client.get_stats()
        memory_count = stats.get("total", 0)

        # Update status pane
        status_pane = self.query_one(StatusPane)
        status_pane.update_status(
            ollama_connected=ollama_connected,
            memory_connected=memory_connected,
            memory_count=memory_count,
            model_name=self.config.ollama_model,
        )

    async def _update_memory_count(self) -> None:
        """Update the memory count in the status pane for the active character."""
        # Get active character
        character_pane = self.query_one(CharacterPane)
        try:
            active_character = character_pane.get_selected_character()
            # Get stats for this specific character (using character.id as user_id filter)
            # Note: OpenMemory doesn't have per-user stats, so we query memories
            memories = await self.memory_client.get_all_for_user(active_character.id)
            memory_count = len(memories)
        except Exception:
            # If we can't get character-specific count, show 0
            memory_count = 0

        status_pane = self.query_one(StatusPane)
        status_pane.update_status(memory_count=memory_count)

    def action_next_character(self) -> None:
        """Navigate to next character."""
        character_pane = self.query_one(CharacterPane)
        character_pane.next_character()

    def action_previous_character(self) -> None:
        """Navigate to previous character."""
        character_pane = self.query_one(CharacterPane)
        character_pane.previous_character()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle user input submission.

        Args:
            event: The Input.Submitted event.
        """
        # Get the input widget
        if event.input.id != "chat-input":
            return

        user_input = event.value.strip()
        if not user_input:
            return

        # Get components
        chat_pane = self.query_one(ChatPane)
        character_pane = self.query_one(CharacterPane)

        # Add user message to chat
        user_message = Message(role=MessageRole.USER, content=user_input)
        chat_pane.add_message(user_message)

        # Clear input and disable it
        chat_pane.clear_input()
        chat_pane.set_input_enabled(False)
        chat_pane.show_typing_indicator()

        try:
            # Get active character
            active_character = character_pane.get_selected_character()
            if not active_character:
                # Use default if no character selected
                active_character = self.character_manager.get_all_characters()[0]

            # Hide typing indicator and create placeholder message for streaming
            chat_pane.hide_typing_indicator()

            # Create initial assistant message (empty content)
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content="",
                metadata={"character_name": active_character.name},
            )
            chat_pane.add_message(assistant_message)

            # Stream response chunks and update message in real-time
            response_text = ""
            async for chunk in self.message_handler.process_message_streaming(
                user_input,
                active_character,
                chat_pane.get_all_messages()[-10:],  # Last 10 messages for context
            ):
                response_text += chunk
                chat_pane.update_last_message(response_text)

            # Final update to ensure complete message is displayed
            chat_pane.update_last_message(response_text, force=True)

            # Update memory count after storing conversation
            await self._update_memory_count()

        except Exception as e:
            # Show error message
            error_message = Message(
                role=MessageRole.SYSTEM,
                content=f"Error: {str(e)}",
            )
            chat_pane.add_message(error_message)

        finally:
            # Re-enable input and restore focus
            chat_pane.set_input_enabled(True)
            chat_pane.focus_input()


def main() -> None:
    """Main entry point for the application."""
    app = WintermuteApp()
    app.run()


if __name__ == "__main__":
    main()
