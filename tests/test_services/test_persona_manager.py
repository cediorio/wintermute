"""Tests for the PersonaManager service."""

from pathlib import Path

import pytest

from wintermute.models.persona import Persona
from wintermute.services.persona_manager import PersonaManager


@pytest.fixture
def personas_dir(tmp_path: Path) -> Path:
    """Create a temporary personas directory with test files."""
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    
    # Create test persona files
    default_persona = {
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
    (personas_dir / "default.json").write_text(json.dumps(default_persona))
    (personas_dir / "technical.json").write_text(json.dumps(technical_persona))
    
    return personas_dir


class TestPersonaManagerInitialization:
    """Test PersonaManager initialization."""

    def test_persona_manager_can_be_created(self, personas_dir: Path):
        """Test that PersonaManager can be instantiated."""
        manager = PersonaManager(personas_dir)
        assert manager is not None

    def test_persona_manager_loads_personas(self, personas_dir: Path):
        """Test that PersonaManager loads personas from directory."""
        manager = PersonaManager(personas_dir)
        
        assert len(manager.personas) == 2
        assert any(p.id == "default" for p in manager.personas)
        assert any(p.id == "technical" for p in manager.personas)


class TestPersonaManagerGetters:
    """Test PersonaManager getter methods."""

    def test_get_persona_by_id(self, personas_dir: Path):
        """Test getting a persona by ID."""
        manager = PersonaManager(personas_dir)
        
        persona = manager.get_persona_by_id("default")
        
        assert persona is not None
        assert persona.id == "default"
        assert persona.name == "Default Assistant"

    def test_get_persona_by_invalid_id(self, personas_dir: Path):
        """Test that getting invalid ID returns None."""
        manager = PersonaManager(personas_dir)
        
        persona = manager.get_persona_by_id("nonexistent")
        
        assert persona is None

    def test_get_all_personas(self, personas_dir: Path):
        """Test getting all personas."""
        manager = PersonaManager(personas_dir)
        
        personas = manager.get_all_personas()
        
        assert len(personas) == 2
        assert personas[0].id in ["default", "technical"]

    def test_get_persona_ids(self, personas_dir: Path):
        """Test getting list of persona IDs."""
        manager = PersonaManager(personas_dir)
        
        ids = manager.get_persona_ids()
        
        assert len(ids) == 2
        assert "default" in ids
        assert "technical" in ids


class TestPersonaManagerActivePersona:
    """Test active persona management."""

    def test_get_active_persona_default(self, personas_dir: Path):
        """Test that first persona is active by default."""
        manager = PersonaManager(personas_dir)
        
        active = manager.get_active_persona()
        
        assert active is not None
        assert active.id in ["default", "technical"]

    def test_set_active_persona_by_id(self, personas_dir: Path):
        """Test setting active persona by ID."""
        manager = PersonaManager(personas_dir)
        
        manager.set_active_persona("technical")
        active = manager.get_active_persona()
        
        assert active.id == "technical"

    def test_set_active_persona_invalid_id(self, personas_dir: Path):
        """Test that setting invalid ID does nothing."""
        manager = PersonaManager(personas_dir)
        original_active = manager.get_active_persona()
        
        manager.set_active_persona("nonexistent")
        
        # Should remain unchanged
        assert manager.get_active_persona().id == original_active.id


class TestPersonaManagerValidation:
    """Test persona validation."""

    def test_load_invalid_json_file(self, tmp_path: Path):
        """Test that invalid JSON files are skipped."""
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()
        
        # Create invalid JSON file
        (personas_dir / "invalid.json").write_text("not valid json{")
        
        # Create valid file
        import json
        valid_persona = {
            "id": "valid",
            "name": "Valid",
            "system_prompt": "Test",
        }
        (personas_dir / "valid.json").write_text(json.dumps(valid_persona))
        
        manager = PersonaManager(personas_dir)
        
        # Should only load the valid one
        assert len(manager.personas) == 1
        assert manager.personas[0].id == "valid"

    def test_load_persona_missing_required_fields(self, tmp_path: Path):
        """Test that personas missing required fields are skipped."""
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()
        
        import json
        # Missing 'system_prompt' field
        invalid_persona = {
            "id": "invalid",
            "name": "Invalid Persona",
        }
        (personas_dir / "invalid.json").write_text(json.dumps(invalid_persona))
        
        manager = PersonaManager(personas_dir)
        
        # Should skip invalid persona
        assert len(manager.personas) == 0


class TestPersonaManagerEmptyDirectory:
    """Test PersonaManager with empty directory."""

    def test_empty_personas_directory(self, tmp_path: Path):
        """Test that empty directory loads no personas."""
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()
        
        manager = PersonaManager(personas_dir)
        
        assert len(manager.personas) == 0

    def test_get_active_persona_when_empty(self, tmp_path: Path):
        """Test that get_active_persona returns None when empty."""
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()
        
        manager = PersonaManager(personas_dir)
        
        active = manager.get_active_persona()
        assert active is None


class TestPersonaManagerReload:
    """Test reloading personas."""

    def test_reload_personas(self, personas_dir: Path):
        """Test reloading personas from directory."""
        manager = PersonaManager(personas_dir)
        original_count = len(manager.personas)
        
        # Add a new persona file
        import json
        new_persona = {
            "id": "creative",
            "name": "Creative Writer",
            "system_prompt": "You are creative.",
        }
        (personas_dir / "creative.json").write_text(json.dumps(new_persona))
        
        manager.reload()
        
        assert len(manager.personas) == original_count + 1
        assert any(p.id == "creative" for p in manager.personas)
