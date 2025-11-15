"""Character creation and editing wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea, Static
from textual.binding import Binding

from wintermute.models.character import Character


class CharacterWizard(ModalScreen[Character | None]):
    """Modal screen for creating or editing a character."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    CSS = """
    CharacterWizard {
        align: center middle;
    }

    #wizard-dialog {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #wizard-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        margin-top: 1;
        text-style: bold;
    }

    Input {
        margin-bottom: 1;
    }

    TextArea {
        height: 8;
        margin-bottom: 1;
    }

    #button-container {
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, character: Character | None = None):
        """
        Initialize the wizard.

        Args:
            character: Existing character to edit, or None for new character.
        """
        super().__init__()
        self.editing_character = character
        self.is_edit_mode = character is not None

    def compose(self) -> ComposeResult:
        """Compose the wizard UI."""
        title = "Edit Character" if self.is_edit_mode else "Create New Character"

        with Container(id="wizard-dialog"):
            yield Label(title, id="wizard-title")

            # Name field
            yield Label("Name:", classes="field-label")
            yield Input(
                placeholder="e.g., Technical Expert",
                id="name-input",
                value=self.editing_character.name if self.editing_character else "",
            )

            # ID field
            yield Label("ID:", classes="field-label")
            yield Input(
                placeholder="e.g., technical (lowercase, no spaces)",
                id="id-input",
                value=self.editing_character.id if self.editing_character else "",
                disabled=self.is_edit_mode,  # Can't change ID when editing
            )

            # Description field
            yield Label("Description:", classes="field-label")
            yield Input(
                placeholder="Brief description of the character",
                id="description-input",
                value=self.editing_character.description if self.editing_character else "",
            )

            # System Prompt field (multiline)
            yield Label("System Prompt:", classes="field-label")
            yield TextArea(
                text=self.editing_character.system_prompt if self.editing_character else "",
                id="system-prompt-input",
            )

            # Temperature field
            yield Label("Temperature:", classes="field-label")
            temp_value = (
                str(self.editing_character.temperature) if self.editing_character else "0.7"
            )
            yield Input(
                placeholder="0.0 to 2.0 (default: 0.7)",
                id="temperature-input",
                value=temp_value,
            )

            # Traits field
            yield Label("Traits (comma-separated):", classes="field-label")
            traits_value = (
                ", ".join(self.editing_character.traits) if self.editing_character else ""
            )
            yield Input(
                placeholder="e.g., analytical, precise, methodical",
                id="traits-input",
                value=traits_value,
            )

            # Buttons
            with Horizontal(id="button-container"):
                yield Button("Cancel", variant="default", id="cancel-button")
                yield Button("Save Character", variant="primary", id="save-button")

    def on_mount(self) -> None:
        """Focus the name input when wizard opens."""
        self.query_one("#name-input", Input).focus()

    def action_cancel(self) -> None:
        """Cancel and close the wizard."""
        self.dismiss(None)

    async def action_save(self) -> None:
        """Save the character."""
        await self._save_character()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "cancel-button":
            self.dismiss(None)
        elif event.button.id == "save-button":
            await self._save_character()

    async def _save_character(self) -> None:
        """Validate and save the character."""
        import sys

        print("🔧 [DEBUG] _save_character called", file=sys.stderr)

        # Get field values
        name = self.query_one("#name-input", Input).value.strip()
        char_id = self.query_one("#id-input", Input).value.strip()
        description = self.query_one("#description-input", Input).value.strip()
        system_prompt = self.query_one("#system-prompt-input", TextArea).text.strip()
        temperature_str = self.query_one("#temperature-input", Input).value.strip()
        traits_str = self.query_one("#traits-input", Input).value.strip()

        print(f"🔧 [DEBUG] Fields - name: {name}, id: {char_id}", file=sys.stderr)
        print(f"🔧 [DEBUG] System prompt length: {len(system_prompt)}", file=sys.stderr)

        # Validate required fields
        if not name:
            self.notify("Name is required", severity="error")
            return

        if not char_id:
            self.notify("ID is required", severity="error")
            return

        if not system_prompt:
            self.notify("System prompt is required", severity="error")
            print("🔧 [DEBUG] Validation failed: empty system prompt", file=sys.stderr)
            return

        # Validate and parse temperature
        try:
            temperature = float(temperature_str) if temperature_str else 0.7
            if not (0.0 <= temperature <= 2.0):
                self.notify("Temperature must be between 0.0 and 2.0", severity="error")
                return
        except ValueError:
            self.notify("Invalid temperature value", severity="error")
            return

        # Parse traits
        traits = [t.strip() for t in traits_str.split(",") if t.strip()] if traits_str else []

        # Create character object
        try:
            character = Character(
                id=char_id,
                name=name,
                system_prompt=system_prompt,
                description=description,
                temperature=temperature,
                traits=traits,
            )

            print(
                f"🔧 [DEBUG] Character object created, dismissing with: {character.name}",
                file=sys.stderr,
            )

            # Return the character to the caller
            self.dismiss(character)

        except Exception as e:
            print(f"🔧 [DEBUG] Exception creating character: {e}", file=sys.stderr)
            self.notify(f"Error creating character: {e}", severity="error")
