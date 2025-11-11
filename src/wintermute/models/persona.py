"""Persona model for defining AI personalities."""

from pydantic import BaseModel, ConfigDict, Field


class Persona(BaseModel):
    """A persona representing an AI personality with specific traits and behavior."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "technical",
                "name": "Technical Expert",
                "description": "Expert in programming and system design",
                "system_prompt": "You are a technical expert...",
                "temperature": 0.5,
                "traits": ["analytical", "precise", "methodical"],
            }
        }
    )

    id: str = Field(..., description="Unique identifier for the persona")
    name: str = Field(..., description="Display name of the persona")
    system_prompt: str = Field(..., description="System prompt that defines persona behavior")
    description: str = Field(default="", description="Human-readable description of the persona")
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature parameter (0.0-2.0)",
    )
    traits: list[str] = Field(
        default_factory=list,
        description="List of personality traits",
    )
