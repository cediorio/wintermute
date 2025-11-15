"""Character manager for loading and managing AI characters."""

import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from wintermute.models.character import Character


class CharacterManager:
    """Manager for loading and switching between AI characters."""

    def __init__(self, characters_dir: Path):
        """
        Initialize the CharacterManager.

        Args:
            characters_dir: Directory containing character JSON files.
        """
        self.characters_dir = Path(characters_dir)
        self.characters: list[Character] = []
        self.active_index = 0
        self.load_characters()

    def load_characters(self) -> None:
        """Load all characters from the characters directory."""
        self.characters = []

        if not self.characters_dir.exists():
            return

        # Load all JSON files in the directory
        for json_file in self.characters_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    character = Character.model_validate(data)
                    self.characters.append(character)
            except (json.JSONDecodeError, ValidationError):
                # Skip invalid files
                continue

    def reload(self) -> None:
        """Reload characters from directory."""
        self.load_characters()

    def get_character_by_id(self, character_id: str) -> Optional[Character]:
        """
        Get a character by its ID.

        Args:
            character_id: The ID of the character to retrieve.

        Returns:
            The Character object if found, None otherwise.
        """
        for character in self.characters:
            if character.id == character_id:
                return character
        return None

    def get_all_characters(self) -> list[Character]:
        """
        Get all loaded characters.

        Returns:
            List of all Character objects.
        """
        return self.characters

    def get_character_ids(self) -> list[str]:
        """
        Get a list of all character IDs.

        Returns:
            List of character ID strings.
        """
        return [p.id for p in self.characters]

    def get_active_character(self) -> Optional[Character]:
        """
        Get the currently active character.

        Returns:
            The active Persona object, or None if no personas loaded.
        """
        if not self.characters:
            return None
        return self.characters[self.active_index]

    def set_active_character(self, character_id: str) -> None:
        """
        Set the active character by ID.

        Args:
            character_id: The ID of the character to activate.
        """
        for i, character in enumerate(self.characters):
            if character.id == character_id:
                self.active_index = i
                return
