"""Persona pane widget for selecting and managing AI personas."""

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from wintermute.models.persona import Persona


class PersonaPane(Widget):
    """Widget for displaying and selecting AI personas."""

    # Reactive property for selected persona index
    selected_index: reactive[int] = reactive(0)

    def __init__(self, personas: list[Persona], **kwargs):
        """
        Initialize the PersonaPane.

        Args:
            personas: List of available personas.
            **kwargs: Additional keyword arguments for Widget.
        """
        super().__init__(**kwargs)
        self.personas = personas

    def get_selected_persona(self) -> Persona:
        """
        Get the currently selected persona.

        Returns:
            The selected Persona object.
        """
        if not self.personas or self.selected_index >= len(self.personas):
            raise IndexError("No personas available")
        
        selected_persona: Persona = self.personas[self.selected_index]
        return selected_persona

    def get_all_personas(self) -> list[Persona]:
        """
        Get all available personas.

        Returns:
            List of all Persona objects.
        """
        return self.personas

    def select_persona(self, index: int) -> None:
        """
        Select a persona by index.

        Args:
            index: The index of the persona to select.
        """
        if 0 <= index < len(self.personas):
            self.selected_index = index

    def select_persona_by_id(self, persona_id: str) -> None:
        """
        Select a persona by its ID.

        Args:
            persona_id: The ID of the persona to select.
        """
        for i, persona in enumerate(self.personas):
            if persona.id == persona_id:
                self.selected_index = i
                return

    def next_persona(self) -> None:
        """Navigate to the next persona (wraps around to beginning)."""
        if self.personas:
            self.selected_index = (self.selected_index + 1) % len(self.personas)

    def previous_persona(self) -> None:
        """Navigate to the previous persona (wraps around to end)."""
        if self.personas:
            self.selected_index = (self.selected_index - 1) % len(self.personas)

    def render(self) -> Text:
        """
        Render the persona list.

        Returns:
            Rich Text object with formatted persona list.
        """
        text = Text()

        # Title
        text.append("Personas\n", style="bold underline")
        text.append("\n")

        if not self.personas:
            text.append("No personas available\n", style="dim")
            return text

        # List all personas
        for i, persona in enumerate(self.personas):
            if i == self.selected_index:
                # Highlight selected persona
                text.append("▶ ", style="bold cyan")
                text.append(f"{persona.name}\n", style="bold cyan")
                
                # Show description for selected persona
                if persona.description:
                    text.append(f"  {persona.description}\n", style="dim italic")
            else:
                text.append(f"  {persona.name}\n")

        return text
