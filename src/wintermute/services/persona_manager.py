"""Persona manager for loading and managing AI personas."""

import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from wintermute.models.persona import Persona


class PersonaManager:
    """Manager for loading and switching between AI personas."""

    def __init__(self, personas_dir: Path):
        """
        Initialize the PersonaManager.

        Args:
            personas_dir: Directory containing persona JSON files.
        """
        self.personas_dir = Path(personas_dir)
        self.personas: list[Persona] = []
        self.active_index = 0
        self.load_personas()

    def load_personas(self) -> None:
        """Load all personas from the personas directory."""
        self.personas = []

        if not self.personas_dir.exists():
            return

        # Load all JSON files in the directory
        for json_file in self.personas_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    persona = Persona.model_validate(data)
                    self.personas.append(persona)
            except (json.JSONDecodeError, ValidationError):
                # Skip invalid files
                continue

    def reload(self) -> None:
        """Reload personas from directory."""
        self.load_personas()

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """
        Get a persona by its ID.

        Args:
            persona_id: The ID of the persona to retrieve.

        Returns:
            The Persona object if found, None otherwise.
        """
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None

    def get_all_personas(self) -> list[Persona]:
        """
        Get all loaded personas.

        Returns:
            List of all Persona objects.
        """
        return self.personas

    def get_persona_ids(self) -> list[str]:
        """
        Get a list of all persona IDs.

        Returns:
            List of persona ID strings.
        """
        return [p.id for p in self.personas]

    def get_active_persona(self) -> Optional[Persona]:
        """
        Get the currently active persona.

        Returns:
            The active Persona object, or None if no personas loaded.
        """
        if not self.personas:
            return None
        return self.personas[self.active_index]

    def set_active_persona(self, persona_id: str) -> None:
        """
        Set the active persona by ID.

        Args:
            persona_id: The ID of the persona to activate.
        """
        for i, persona in enumerate(self.personas):
            if persona.id == persona_id:
                self.active_index = i
                return
