"""Tests for the Character model."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from wintermute.models.character import Character


class TestPersonaCreation:
    """Test character creation with valid data."""

    def test_persona_creation_with_valid_data_succeeds(
        self, sample_persona_data: dict
    ) -> None:
        """Test that a character can be created with valid data."""
        character = Character(**sample_persona_data)

        assert character.id == "test"
        assert character.name == "Test Character"
        assert character.description == "A test character"
        assert character.system_prompt == "You are a test assistant."
        assert character.temperature == 0.7
        assert character.traits == ["test", "helpful"]

    def test_persona_creation_with_minimal_data_succeeds(self) -> None:
        """Test that a character can be created with only required fields."""
        character = Character(
            id="minimal",
            name="Minimal Character",
            system_prompt="You are minimal.",
        )

        assert character.id == "minimal"
        assert character.name == "Minimal Character"
        assert character.system_prompt == "You are minimal."
        # Check default values
        assert character.temperature == 0.7
        assert character.description == ""
        assert character.traits == []


class TestPersonaValidation:
    """Test character validation rules."""

    def test_persona_creation_missing_id_raises_error(self) -> None:
        """Test that creating a character without ID raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Character(
                name="Test",
                system_prompt="Test prompt",
            )
        
        assert "id" in str(exc_info.value).lower()

    def test_persona_creation_missing_name_raises_error(self) -> None:
        """Test that creating a character without name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Character(
                id="test",
                system_prompt="Test prompt",
            )
        
        assert "name" in str(exc_info.value).lower()

    def test_persona_creation_missing_system_prompt_raises_error(self) -> None:
        """Test that creating a character without system_prompt raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Character(
                id="test",
                name="Test",
            )
        
        assert "system_prompt" in str(exc_info.value).lower()

    def test_persona_temperature_bounds_validation(self) -> None:
        """Test that temperature is validated to be between 0.0 and 2.0."""
        # Temperature too low
        with pytest.raises(ValidationError):
            Character(
                id="test",
                name="Test",
                system_prompt="Test",
                temperature=-0.1,
            )
        
        # Temperature too high
        with pytest.raises(ValidationError):
            Character(
                id="test",
                name="Test",
                system_prompt="Test",
                temperature=2.1,
            )
        
        # Valid boundaries should work
        persona_low = Character(
            id="test1",
            name="Test",
            system_prompt="Test",
            temperature=0.0,
        )
        assert persona_low.temperature == 0.0

        persona_high = Character(
            id="test2",
            name="Test",
            system_prompt="Test",
            temperature=2.0,
        )
        assert persona_high.temperature == 2.0


class TestPersonaSerialization:
    """Test character serialization to/from JSON."""

    def test_persona_serialization_to_dict(self, sample_persona_data: dict) -> None:
        """Test that a character can be serialized to a dictionary."""
        character = Character(**sample_persona_data)
        persona_dict = character.model_dump()

        assert persona_dict["id"] == "test"
        assert persona_dict["name"] == "Test Character"
        assert persona_dict["description"] == "A test character"
        assert persona_dict["system_prompt"] == "You are a test assistant."
        assert persona_dict["temperature"] == 0.7
        assert persona_dict["traits"] == ["test", "helpful"]

    def test_persona_serialization_to_json(self, sample_persona_data: dict) -> None:
        """Test that a character can be serialized to JSON string."""
        character = Character(**sample_persona_data)
        persona_json = character.model_dump_json()

        # Parse back to verify
        parsed = json.loads(persona_json)
        assert parsed["id"] == "test"
        assert parsed["name"] == "Test Character"

    def test_persona_deserialization_from_dict(self, sample_persona_data: dict) -> None:
        """Test that a character can be created from a dictionary."""
        character = Character.model_validate(sample_persona_data)

        assert character.id == "test"
        assert character.name == "Test Character"

    def test_persona_deserialization_from_json(self, sample_persona_data: dict) -> None:
        """Test that a character can be created from JSON string."""
        persona_json = json.dumps(sample_persona_data)
        character = Character.model_validate_json(persona_json)

        assert character.id == "test"
        assert character.name == "Test Character"

    def test_persona_roundtrip_serialization(self, sample_persona_data: dict) -> None:
        """Test that serialization and deserialization preserve data."""
        original = Character(**sample_persona_data)
        
        # Dict roundtrip
        dict_data = original.model_dump()
        from_dict = Character.model_validate(dict_data)
        assert original == from_dict
        
        # JSON roundtrip
        json_data = original.model_dump_json()
        from_json = Character.model_validate_json(json_data)
        assert original == from_json


class TestPersonaDefaultValues:
    """Test default values for optional character fields."""

    def test_default_temperature_is_0_7(self) -> None:
        """Test that default temperature is 0.7."""
        character = Character(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert character.temperature == 0.7

    def test_default_description_is_empty_string(self) -> None:
        """Test that default description is empty string."""
        character = Character(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert character.description == ""

    def test_default_traits_is_empty_list(self) -> None:
        """Test that default traits is empty list."""
        character = Character(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert character.traits == []
