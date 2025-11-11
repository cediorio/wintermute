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
from wintermute.services.persona_manager import PersonaManager
from wintermute.ui.chat_pane import ChatPane
from wintermute.ui.persona_pane import PersonaPane
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
    
    #persona-pane {
        height: 60%;
    }
    
    #status-pane {
        height: 40%;
    }
    
    ChatPane {
        border: solid green;
        padding: 1;
    }
    
    PersonaPane {
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
        Binding("ctrl+p", "next_persona", "Next Persona"),
        Binding("ctrl+n", "previous_persona", "Previous Persona"),
    ]

    def __init__(self):
        """Initialize the Wintermute application."""
        super().__init__()
        
        # Load configuration
        self.config = Config()
        
        # Initialize services
        self.ollama_client = OllamaClient(self.config)
        self.memory_client = MemoryClient(self.config)
        
        # Initialize persona manager
        personas_dir = Path(__file__).parent.parent.parent / "personas"
        self.persona_manager = PersonaManager(personas_dir)
        
        # Initialize message handler
        self.message_handler = MessageHandler(
            self.ollama_client,
            self.memory_client,
            self.config.user_id,
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
            yield PersonaPane(
                self.persona_manager.get_all_personas(),
                id="persona-pane"
            )
            yield StatusPane(id="status-pane")

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Check service connections
        await self._check_connections()

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

    def action_next_persona(self) -> None:
        """Navigate to next persona."""
        persona_pane = self.query_one(PersonaPane)
        persona_pane.next_persona()

    def action_previous_persona(self) -> None:
        """Navigate to previous persona."""
        persona_pane = self.query_one(PersonaPane)
        persona_pane.previous_persona()

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
        persona_pane = self.query_one(PersonaPane)

        # Add user message to chat
        user_message = Message(role=MessageRole.USER, content=user_input)
        chat_pane.add_message(user_message)

        # Clear input and disable it
        chat_pane.clear_input()
        chat_pane.set_input_enabled(False)
        chat_pane.show_typing_indicator()

        try:
            # Get active persona
            active_persona = persona_pane.get_selected_persona()
            if not active_persona:
                # Use default if no persona selected
                active_persona = self.persona_manager.get_all_personas()[0]

            # Process message and stream response
            response_text = ""
            async for chunk in self.message_handler.process_message_streaming(
                user_input,
                active_persona,
                chat_pane.get_all_messages()[-10:],  # Last 10 messages for context
            ):
                response_text += chunk

            # Add assistant response to chat
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=response_text,
                metadata={"persona_name": active_persona.name},
            )
            chat_pane.add_message(assistant_message)

        except Exception as e:
            # Show error message
            error_message = Message(
                role=MessageRole.SYSTEM,
                content=f"Error: {str(e)}",
            )
            chat_pane.add_message(error_message)

        finally:
            # Re-enable input and hide typing indicator
            chat_pane.hide_typing_indicator()
            chat_pane.set_input_enabled(True)


def main() -> None:
    """Main entry point for the application."""
    app = WintermuteApp()
    app.run()


if __name__ == "__main__":
    main()
