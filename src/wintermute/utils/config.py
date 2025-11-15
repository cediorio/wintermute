"""Configuration management for Wintermute."""

from typing import Optional

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Ollama Configuration
    ollama_url: HttpUrl = Field(
        default="http://localhost:11434",
        description="URL of the Ollama API server",
    )
    ollama_model: str = Field(
        default="llama2",
        description="Ollama model to use for chat completions",
    )

    # OpenMemory Configuration
    openmemory_url: HttpUrl = Field(
        default="http://localhost:8080",
        description="URL of the OpenMemory API server",
    )
    openmemory_api_key: Optional[str] = Field(
        default=None,
        description="API key for OpenMemory (if required)",
    )

    # Application Settings
    default_character: str = Field(
        default="default",
        description="Default character ID to use on startup",
    )
    max_memory_items: int = Field(
        default=100,
        gt=0,
        description="Maximum number of memory items to retrieve",
    )
    global_system_prompt: str = Field(
        default=(
            "You are engaging in a conversation as a character with a distinct personality. "
            "While you can be helpful and provide assistance, you are meant to approximate "
            "talking with a real person with your own perspectives, experiences, and manner of speaking. "
            "Never break character by saying you are an AI, artificial intelligence, or language model. "
            "Stay true to your character's personality and background."
        ),
        description="Global system prompt prepended to all character prompts",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    @field_validator("openmemory_api_key", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty string to None for optional API key."""
        if v == "":
            return None
        return v

    def __repr__(self) -> str:
        """Return string representation without exposing sensitive data."""
        return (
            f"Config("
            f"ollama_url={self.ollama_url}, "
            f"ollama_model={self.ollama_model}, "
            f"openmemory_url={self.openmemory_url}, "
            f"openmemory_api_key={'***' if self.openmemory_api_key else None}, "
            f"default_character={self.default_character}, "
            f"debug={self.debug})"
        )

    def __str__(self) -> str:
        """Return user-friendly string representation."""
        return self.__repr__()
