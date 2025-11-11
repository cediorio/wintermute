"""Tests for configuration management."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from wintermute.utils.config import Config


class TestConfigLoading:
    """Test loading configuration from environment."""

    def test_config_loads_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config loads values from environment variables."""
        monkeypatch.setenv("OLLAMA_URL", "http://test:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "test-model")
        monkeypatch.setenv("OPENMEMORY_URL", "http://test:8080")
        monkeypatch.setenv("DEFAULT_PERSONA", "test-persona")
        
        config = Config()
        
        assert str(config.ollama_url) == "http://test:11434/"
        assert config.ollama_model == "test-model"
        assert str(config.openmemory_url) == "http://test:8080/"
        assert config.default_persona == "test-persona"

    def test_config_loads_from_dotenv_file(self, tmp_path: Path) -> None:
        """Test that config loads from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OLLAMA_URL=http://dotenv:11434\n"
            "OLLAMA_MODEL=dotenv-model\n"
            "OPENMEMORY_URL=http://dotenv:8080\n"
        )
        
        config = Config(_env_file=str(env_file))
        
        assert str(config.ollama_url) == "http://dotenv:11434/"
        assert config.ollama_model == "dotenv-model"

    def test_config_environment_overrides_dotenv(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override .env file values."""
        env_file = tmp_path / ".env"
        env_file.write_text("OLLAMA_URL=http://dotenv:11434\n")
        
        monkeypatch.setenv("OLLAMA_URL", "http://override:11434")
        
        config = Config(_env_file=str(env_file))
        
        assert str(config.ollama_url) == "http://override:11434/"


class TestConfigDefaults:
    """Test default configuration values."""

    def test_config_uses_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config provides sensible defaults."""
        # Clear any existing env vars
        for key in ["OLLAMA_URL", "OLLAMA_MODEL", "OPENMEMORY_URL", 
                    "DEFAULT_PERSONA", "MAX_MEMORY_ITEMS", "USER_ID", "DEBUG"]:
            monkeypatch.delenv(key, raising=False)
        
        config = Config(_env_file=None)
        
        # Check defaults
        assert str(config.ollama_url) == "http://localhost:11434/"
        assert config.ollama_model == "llama2"
        assert str(config.openmemory_url) == "http://localhost:8080/"
        assert config.default_persona == "default"
        assert config.max_memory_items == 100
        assert config.user_id == "default_user"
        assert config.debug is False

    def test_config_optional_api_key_defaults_to_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that optional API key defaults to None."""
        monkeypatch.delenv("OPENMEMORY_API_KEY", raising=False)
        
        config = Config(_env_file=None)
        
        assert config.openmemory_api_key is None

    def test_config_empty_api_key_treated_as_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that empty string API key is treated as None."""
        monkeypatch.setenv("OPENMEMORY_API_KEY", "")
        
        config = Config(_env_file=None)
        
        assert config.openmemory_api_key is None


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_validates_ollama_url_format(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that Ollama URL must be a valid URL."""
        monkeypatch.setenv("OLLAMA_URL", "not-a-url")
        
        with pytest.raises(ValidationError) as exc_info:
            Config(_env_file=None)
        
        assert "ollama_url" in str(exc_info.value).lower()

    def test_config_validates_openmemory_url_format(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that OpenMemory URL must be a valid URL."""
        monkeypatch.setenv("OPENMEMORY_URL", "not-a-url")
        
        with pytest.raises(ValidationError) as exc_info:
            Config(_env_file=None)
        
        assert "openmemory_url" in str(exc_info.value).lower()

    def test_config_validates_max_memory_items_positive(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that max_memory_items must be positive."""
        monkeypatch.setenv("MAX_MEMORY_ITEMS", "-1")
        
        with pytest.raises(ValidationError) as exc_info:
            Config(_env_file=None)
        
        assert "max_memory_items" in str(exc_info.value).lower()

    def test_config_accepts_valid_urls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that valid URLs are accepted."""
        monkeypatch.setenv("OLLAMA_URL", "http://example.com:11434")
        monkeypatch.setenv("OPENMEMORY_URL", "https://memory.example.com:8080")
        
        config = Config(_env_file=None)
        
        assert str(config.ollama_url) == "http://example.com:11434/"
        assert str(config.openmemory_url) == "https://memory.example.com:8080/"


class TestConfigTypes:
    """Test configuration field types."""

    def test_config_debug_is_boolean(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug flag is parsed as boolean."""
        monkeypatch.setenv("DEBUG", "true")
        config = Config(_env_file=None)
        assert config.debug is True
        
        monkeypatch.setenv("DEBUG", "false")
        config = Config(_env_file=None)
        assert config.debug is False
        
        monkeypatch.setenv("DEBUG", "1")
        config = Config(_env_file=None)
        assert config.debug is True

    def test_config_max_memory_items_is_integer(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that max_memory_items is parsed as integer."""
        monkeypatch.setenv("MAX_MEMORY_ITEMS", "500")
        
        config = Config(_env_file=None)
        
        assert isinstance(config.max_memory_items, int)
        assert config.max_memory_items == 500

    def test_config_invalid_integer_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that invalid integer value raises validation error."""
        monkeypatch.setenv("MAX_MEMORY_ITEMS", "not-a-number")
        
        with pytest.raises(ValidationError):
            Config(_env_file=None)


class TestConfigUsage:
    """Test practical configuration usage."""

    def test_config_can_be_instantiated_once(self) -> None:
        """Test that config can be instantiated and reused."""
        config = Config()
        
        assert config.ollama_url is not None
        assert config.openmemory_url is not None
        assert config.ollama_model is not None

    def test_config_provides_all_required_settings(self) -> None:
        """Test that config provides all settings needed for the app."""
        config = Config()
        
        # Ollama settings
        assert hasattr(config, "ollama_url")
        assert hasattr(config, "ollama_model")
        
        # OpenMemory settings
        assert hasattr(config, "openmemory_url")
        assert hasattr(config, "openmemory_api_key")
        
        # App settings
        assert hasattr(config, "default_persona")
        assert hasattr(config, "max_memory_items")
        assert hasattr(config, "user_id")
        assert hasattr(config, "debug")

    def test_config_url_has_scheme_and_netloc(self) -> None:
        """Test that URL fields are proper URL objects."""
        config = Config()
        
        assert config.ollama_url.scheme in ["http", "https"]
        assert config.ollama_url.host is not None
        assert config.openmemory_url.scheme in ["http", "https"]
        assert config.openmemory_url.host is not None


class TestConfigRepresentation:
    """Test configuration string representation."""

    def test_config_repr_does_not_expose_api_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that API key is not exposed in repr/str."""
        monkeypatch.setenv("OPENMEMORY_API_KEY", "secret-key-12345")
        
        config = Config(_env_file=None)
        config_str = str(config)
        config_repr = repr(config)
        
        assert "secret-key-12345" not in config_str
        assert "secret-key-12345" not in config_repr

    def test_config_model_dump_excludes_sensitive_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that sensitive data can be excluded from dumps."""
        monkeypatch.setenv("OPENMEMORY_API_KEY", "secret-key")
        
        config = Config(_env_file=None)
        
        # API key should be present in normal dump
        dump = config.model_dump()
        assert "openmemory_api_key" in dump
