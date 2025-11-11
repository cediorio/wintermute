"""Message model for chat conversations."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """A message in a conversation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T12:00:00",
                "metadata": {"persona_id": "default"},
            }
        }
    )

    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the message was created",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the message",
    )

    def format_for_display(self) -> str:
        """
        Format the message for display in the TUI.

        Returns:
            Formatted string representation of the message.
        """
        # Use persona name from metadata if available, otherwise use role
        sender = self.metadata.get("persona_name", self.role.value.capitalize())
        time_str = self.timestamp.strftime("%H:%M")
        
        return f"[{time_str}] {sender}: {self.content}"
