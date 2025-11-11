"""Pytest configuration and shared fixtures for Wintermute tests."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def personas_dir(project_root: Path) -> Path:
    """Return the personas directory."""
    return project_root / "personas"


@pytest.fixture
def sample_persona_data() -> dict:
    """Return sample persona data for testing."""
    return {
        "id": "test",
        "name": "Test Persona",
        "description": "A test persona",
        "system_prompt": "You are a test assistant.",
        "temperature": 0.7,
        "traits": ["test", "helpful"],
    }
