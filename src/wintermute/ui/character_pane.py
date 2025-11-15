"""Character pane widget for selecting and managing AI characters."""

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from wintermute.models.character import Character


class CharacterPane(Widget):
    """Widget for displaying and selecting AI characters."""

    # Reactive property for selected character index
    selected_index: reactive[int] = reactive(0)

    def __init__(self, characters: list[Character], **kwargs):
        """
        Initialize the CharacterPane.

        Args:
            characters: List of available characters.
            **kwargs: Additional keyword arguments for Widget.
        """
        super().__init__(**kwargs)
        self.characters = characters

    def get_selected_character(self) -> Character:
        """
        Get the currently selected character.

        Returns:
            The selected Character object.
        """
        if not self.characters or self.selected_index >= len(self.characters):
            raise IndexError("No characters available")

        selected_character: Character = self.characters[self.selected_index]
        return selected_character

    def get_all_characters(self) -> list[Character]:
        """
        Get all available characters.

        Returns:
            List of all Character objects.
        """
        return self.characters

    def select_character(self, index: int) -> None:
        """
        Select a character by index.

        Args:
            index: The index of the character to select.
        """
        if 0 <= index < len(self.characters):
            self.selected_index = index

    def select_character_by_id(self, character_id: str) -> None:
        """
        Select a character by its ID.

        Args:
            character_id: The ID of the character to select.
        """
        for i, character in enumerate(self.characters):
            if character.id == character_id:
                self.selected_index = i
                return

    def next_character(self) -> None:
        """Navigate to the next character (wraps around to beginning)."""
        if self.characters:
            self.selected_index = (self.selected_index + 1) % len(self.characters)

    def previous_character(self) -> None:
        """Navigate to the previous character (wraps around to end)."""
        if self.characters:
            self.selected_index = (self.selected_index - 1) % len(self.characters)

    def render(self) -> Text:
        """
        Render the character list.

        Returns:
            Rich Text object with formatted character list.
        """
        text = Text()

        # Title
        text.append("Characters\n", style="bold underline")
        text.append("\n")

        if not self.characters:
            text.append("No characters available\n", style="dim")
            return text

        # List all characters
        for i, character in enumerate(self.characters):
            if i == self.selected_index:
                # Highlight selected character
                text.append("▶ ", style="bold cyan")
                text.append(f"{character.name}\n", style="bold cyan")

                # Show description for selected character
                if character.description:
                    text.append(f"  {character.description}\n", style="dim italic")
            else:
                text.append(f"  {character.name}\n")

        return text
