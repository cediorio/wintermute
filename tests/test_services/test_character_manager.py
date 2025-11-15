"""Tests for the CharacterManager service."""

from pathlib import Path

import pytest

from wintermute.models.character import Character
from wintermute.services.character_manager import CharacterManager


@pytest.fixture
def characters_dir(tmp_path: Path) -> Path:
    """Create a temporary characters directory with test files."""
    characters_dir = tmp_path / "characters"
    characters_dir.mkdir()
    
    # Create test character files
    default_character = {
        "id": "default",
        "name": "Default Assistant",
        "system_prompt": "You are helpful.",
        "description": "A balanced assistant",
        "temperature": 0.7,
        "traits": ["helpful", "friendly"]
    }
    
    technical_persona = {
        "id": "technical",
        "name": "Technical Expert",
        "system_prompt": "You are technical.",
        "description": "Expert in programming",
        "temperature": 0.5,
        "traits": ["analytical", "precise"]
    }
    
    import json
    (characters_dir / "default.json").write_text(json.dumps(default_character))
    (characters_dir / "technical.json").write_text(json.dumps(technical_persona))
    
    return characters_dir


class TestCharacterManagerInitialization:
    """Test CharacterManager initialization."""

    def test_persona_manager_can_be_created(self, characters_dir: Path):
        """Test that CharacterManager can be instantiated."""
        manager = CharacterManager(characters_dir)
        assert manager is not None

    def test_persona_manager_loads_characters(self, characters_dir: Path):
        """Test that CharacterManager loads characters from directory."""
        manager = CharacterManager(characters_dir)
        
        assert len(manager.characters) == 2
        assert any(p.id == "default" for p in manager.characters)
        assert any(p.id == "technical" for p in manager.characters)


class TestCharacterManagerGetters:
    """Test CharacterManager getter methods."""

    def test_get_character_by_id(self, characters_dir: Path):
        """Test getting a character by ID."""
        manager = CharacterManager(characters_dir)
        
        character = manager.get_persona_by_id("default")
        
        assert character is not None
        assert character.id == "default"
        assert character.name == "Default Assistant"

    def test_get_character_by_invalid_id(self, characters_dir: Path):
        """Test that getting invalid ID returns None."""
        manager = CharacterManager(characters_dir)
        
        character = manager.get_persona_by_id("nonexistent")
        
        assert character is None

    def test_get_all_characters(self, characters_dir: Path):
        """Test getting all characters."""
        manager = CharacterManager(characters_dir)
        
        characters = manager.get_all_characters()
        
        assert len(characters) == 2
        assert characters[0].id in ["default", "technical"]

    def test_get_character_ids(self, characters_dir: Path):
        """Test getting list of character IDs."""
        manager = CharacterManager(characters_dir)
        
        ids = manager.get_persona_ids()
        
        assert len(ids) == 2
        assert "default" in ids
        assert "technical" in ids


class TestCharacterManagerActivePersona:
    """Test active character management."""

    def test_get_active_character_default(self, characters_dir: Path):
        """Test that first character is active by default."""
        manager = CharacterManager(characters_dir)
        
        active = manager.get_active_persona()
        
        assert active is not None
        assert active.id in ["default", "technical"]

    def test_set_active_character_by_id(self, characters_dir: Path):
        """Test setting active character by ID."""
        manager = CharacterManager(characters_dir)
        
        manager.set_active_persona("technical")
        active = manager.get_active_persona()
        
        assert active.id == "technical"

    def test_set_active_character_invalid_id(self, characters_dir: Path):
        """Test that setting invalid ID does nothing."""
        manager = CharacterManager(characters_dir)
        original_active = manager.get_active_persona()
        
        manager.set_active_persona("nonexistent")
        
        # Should remain unchanged
        assert manager.get_active_persona().id == original_active.id


class TestCharacterManagerValidation:
    """Test character validation."""

    def test_load_invalid_json_file(self, tmp_path: Path):
        """Test that invalid JSON files are skipped."""
        characters_dir = tmp_path / "characters"
        characters_dir.mkdir()
        
        # Create invalid JSON file
        (characters_dir / "invalid.json").write_text("not valid json{")
        
        # Create valid file
        import json
        valid_persona = {
            "id": "valid",
            "name": "Valid",
            "system_prompt": "Test",
        }
        (characters_dir / "valid.json").write_text(json.dumps(valid_persona))
        
        manager = CharacterManager(characters_dir)
        
        # Should only load the valid one
        assert len(manager.characters) == 1
        assert manager.characters[0].id == "valid"

    def test_load_persona_missing_required_fields(self, tmp_path: Path):
        """Test that characters missing required fields are skipped."""
        characters_dir = tmp_path / "characters"
        characters_dir.mkdir()
        
        import json
        # Missing 'system_prompt' field
        invalid_persona = {
            "id": "invalid",
            "name": "Invalid Character",
        }
        (characters_dir / "invalid.json").write_text(json.dumps(invalid_persona))
        
        manager = CharacterManager(characters_dir)
        
        # Should skip invalid character
        assert len(manager.characters) == 0


class TestCharacterManagerEmptyDirectory:
    """Test CharacterManager with empty directory."""

    def test_empty_characters_directory(self, tmp_path: Path):
        """Test that empty directory loads no characters."""
        characters_dir = tmp_path / "characters"
        characters_dir.mkdir()
        
        manager = CharacterManager(characters_dir)
        
        assert len(manager.characters) == 0

    def test_get_active_character_when_empty(self, tmp_path: Path):
        """Test that get_active_persona returns None when empty."""
        characters_dir = tmp_path / "characters"
        characters_dir.mkdir()
        
        manager = CharacterManager(characters_dir)
        
        active = manager.get_active_persona()
        assert active is None


class TestCharacterManagerReload:
    """Test reloading characters."""

    def test_reload_characters(self, characters_dir: Path):
        """Test reloading characters from directory."""
        manager = CharacterManager(characters_dir)
        original_count = len(manager.characters)
        
        # Add a new character file
        import json
        new_persona = {
            "id": "creative",
            "name": "Creative Writer",
            "system_prompt": "You are creative.",
        }
        (characters_dir / "creative.json").write_text(json.dumps(new_persona))
        
        manager.reload()
        
        assert len(manager.characters) == original_count + 1
        assert any(p.id == "creative" for p in manager.characters)
