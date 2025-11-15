"""Demo script to show Wintermute UI without requiring external services."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header

from wintermute.models.message import Message, MessageRole
from wintermute.models.character import Character
from wintermute.ui.chat_pane import ChatPane
from wintermute.ui.persona_pane import PersonaPane
from wintermute.ui.status_pane import StatusPane


class WintermuteDemoApp(App):
    """Demo Wintermute app with mock data."""

    TITLE = "Wintermute Demo"
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
    
    PersonaPane {
        border: solid cyan;
        padding: 1;
    }
    
    StatusPane {
        border: solid yellow;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the demo layout."""
        yield Header()
        yield Footer()

        with Container(id="chat-container"):
            yield ChatPane(id="chat")

        with Vertical(id="right-container"):
            # Load characters
            characters = self._load_demo_characters()
            yield PersonaPane(characters, id="character-pane")
            yield StatusPane(id="status-pane")

    def _load_demo_characters(self) -> list[Character]:
        """Load characters from JSON files."""
        import json
        characters_dir = Path(__file__).parent / "characters"
        characters = []
        
        if characters_dir.exists():
            for json_file in characters_dir.glob("*.json"):
                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)
                        character = Character.model_validate(data)
                        characters.append(character)
                except Exception:
                    pass
        
        return characters

    async def on_mount(self) -> None:
        """Set up demo data when app mounts."""
        # Add some demo messages
        chat_pane = self.query_one(ChatPane)
        chat_pane.add_message(
            Message(role=MessageRole.SYSTEM, content="Welcome to Wintermute!")
        )
        chat_pane.add_message(
            Message(role=MessageRole.USER, content="Hello! Can you help me?")
        )
        chat_pane.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content="Of course! I'm here to assist you. What would you like to know?",
            )
        )

        # Update status pane with demo data
        status_pane = self.query_one(StatusPane)
        status_pane.update_status(
            ollama_connected=True,
            memory_connected=True,
            memory_count=42,
            model_name="mannix/llama3.1-8b-abliterated",
        )


if __name__ == "__main__":
    app = WintermuteDemoApp()
    app.run()
