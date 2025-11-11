"""Tests for the Persona model."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from wintermute.models.persona import Persona


class TestPersonaCreation:
    """Test persona creation with valid data."""

    def test_persona_creation_with_valid_data_succeeds(
        self, sample_persona_data: dict
    ) -> None:
        """Test that a persona can be created with valid data."""
        persona = Persona(**sample_persona_data)

        assert persona.id == "test"
        assert persona.name == "Test Persona"
        assert persona.description == "A test persona"
        assert persona.system_prompt == "You are a test assistant."
        assert persona.temperature == 0.7
        assert persona.traits == ["test", "helpful"]

    def test_persona_creation_with_minimal_data_succeeds(self) -> None:
        """Test that a persona can be created with only required fields."""
        persona = Persona(
            id="minimal",
            name="Minimal Persona",
            system_prompt="You are minimal.",
        )

        assert persona.id == "minimal"
        assert persona.name == "Minimal Persona"
        assert persona.system_prompt == "You are minimal."
        # Check default values
        assert persona.temperature == 0.7
        assert persona.description == ""
        assert persona.traits == []


class TestPersonaValidation:
    """Test persona validation rules."""

    def test_persona_creation_missing_id_raises_error(self) -> None:
        """Test that creating a persona without ID raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Persona(
                name="Test",
                system_prompt="Test prompt",
            )
        
        assert "id" in str(exc_info.value).lower()

    def test_persona_creation_missing_name_raises_error(self) -> None:
        """Test that creating a persona without name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Persona(
                id="test",
                system_prompt="Test prompt",
            )
        
        assert "name" in str(exc_info.value).lower()

    def test_persona_creation_missing_system_prompt_raises_error(self) -> None:
        """Test that creating a persona without system_prompt raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Persona(
                id="test",
                name="Test",
            )
        
        assert "system_prompt" in str(exc_info.value).lower()

    def test_persona_temperature_bounds_validation(self) -> None:
        """Test that temperature is validated to be between 0.0 and 2.0."""
        # Temperature too low
        with pytest.raises(ValidationError):
            Persona(
                id="test",
                name="Test",
                system_prompt="Test",
                temperature=-0.1,
            )
        
        # Temperature too high
        with pytest.raises(ValidationError):
            Persona(
                id="test",
                name="Test",
                system_prompt="Test",
                temperature=2.1,
            )
        
        # Valid boundaries should work
        persona_low = Persona(
            id="test1",
            name="Test",
            system_prompt="Test",
            temperature=0.0,
        )
        assert persona_low.temperature == 0.0

        persona_high = Persona(
            id="test2",
            name="Test",
            system_prompt="Test",
            temperature=2.0,
        )
        assert persona_high.temperature == 2.0


class TestPersonaSerialization:
    """Test persona serialization to/from JSON."""

    def test_persona_serialization_to_dict(self, sample_persona_data: dict) -> None:
        """Test that a persona can be serialized to a dictionary."""
        persona = Persona(**sample_persona_data)
        persona_dict = persona.model_dump()

        assert persona_dict["id"] == "test"
        assert persona_dict["name"] == "Test Persona"
        assert persona_dict["description"] == "A test persona"
        assert persona_dict["system_prompt"] == "You are a test assistant."
        assert persona_dict["temperature"] == 0.7
        assert persona_dict["traits"] == ["test", "helpful"]

    def test_persona_serialization_to_json(self, sample_persona_data: dict) -> None:
        """Test that a persona can be serialized to JSON string."""
        persona = Persona(**sample_persona_data)
        persona_json = persona.model_dump_json()

        # Parse back to verify
        parsed = json.loads(persona_json)
        assert parsed["id"] == "test"
        assert parsed["name"] == "Test Persona"

    def test_persona_deserialization_from_dict(self, sample_persona_data: dict) -> None:
        """Test that a persona can be created from a dictionary."""
        persona = Persona.model_validate(sample_persona_data)

        assert persona.id == "test"
        assert persona.name == "Test Persona"

    def test_persona_deserialization_from_json(self, sample_persona_data: dict) -> None:
        """Test that a persona can be created from JSON string."""
        persona_json = json.dumps(sample_persona_data)
        persona = Persona.model_validate_json(persona_json)

        assert persona.id == "test"
        assert persona.name == "Test Persona"

    def test_persona_roundtrip_serialization(self, sample_persona_data: dict) -> None:
        """Test that serialization and deserialization preserve data."""
        original = Persona(**sample_persona_data)
        
        # Dict roundtrip
        dict_data = original.model_dump()
        from_dict = Persona.model_validate(dict_data)
        assert original == from_dict
        
        # JSON roundtrip
        json_data = original.model_dump_json()
        from_json = Persona.model_validate_json(json_data)
        assert original == from_json


class TestPersonaDefaultValues:
    """Test default values for optional persona fields."""

    def test_default_temperature_is_0_7(self) -> None:
        """Test that default temperature is 0.7."""
        persona = Persona(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert persona.temperature == 0.7

    def test_default_description_is_empty_string(self) -> None:
        """Test that default description is empty string."""
        persona = Persona(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert persona.description == ""

    def test_default_traits_is_empty_list(self) -> None:
        """Test that default traits is empty list."""
        persona = Persona(
            id="test",
            name="Test",
            system_prompt="Test",
        )
        assert persona.traits == []
