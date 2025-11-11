"""Tests for the Message model."""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from wintermute.models.message import Message, MessageRole


class TestMessageCreation:
    """Test message creation with different roles."""

    def test_message_creation_user_role_succeeds(self) -> None:
        """Test that a user message can be created."""
        message = Message(
            role=MessageRole.USER,
            content="Hello, how are you?",
        )

        assert message.role == MessageRole.USER
        assert message.content == "Hello, how are you?"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}

    def test_message_creation_assistant_role_succeeds(self) -> None:
        """Test that an assistant message can be created."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="I'm doing well, thank you!",
        )

        assert message.role == MessageRole.ASSISTANT
        assert message.content == "I'm doing well, thank you!"
        assert isinstance(message.timestamp, datetime)

    def test_message_creation_system_role_succeeds(self) -> None:
        """Test that a system message can be created."""
        message = Message(
            role=MessageRole.SYSTEM,
            content="Conversation started.",
        )

        assert message.role == MessageRole.SYSTEM
        assert message.content == "Conversation started."


class TestMessageTimestamp:
    """Test automatic timestamp generation."""

    def test_message_timestamp_generated_automatically(self) -> None:
        """Test that timestamp is automatically generated if not provided."""
        before = datetime.now()
        message = Message(
            role=MessageRole.USER,
            content="Test",
        )
        after = datetime.now()

        assert before <= message.timestamp <= after

    def test_message_timestamp_can_be_provided(self) -> None:
        """Test that a custom timestamp can be provided."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        message = Message(
            role=MessageRole.USER,
            content="Test",
            timestamp=custom_time,
        )

        assert message.timestamp == custom_time


class TestMessageMetadata:
    """Test message metadata handling."""

    def test_message_default_metadata_is_empty_dict(self) -> None:
        """Test that default metadata is an empty dictionary."""
        message = Message(
            role=MessageRole.USER,
            content="Test",
        )

        assert message.metadata == {}
        assert isinstance(message.metadata, dict)

    def test_message_can_have_custom_metadata(self) -> None:
        """Test that messages can have custom metadata."""
        metadata = {
            "persona_id": "technical",
            "memory_count": 5,
            "context_used": True,
        }
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata=metadata,
        )

        assert message.metadata == metadata
        assert message.metadata["persona_id"] == "technical"
        assert message.metadata["memory_count"] == 5


class TestMessageValidation:
    """Test message validation rules."""

    def test_message_creation_missing_role_raises_error(self) -> None:
        """Test that creating a message without role raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Message(content="Test")
        
        assert "role" in str(exc_info.value).lower()

    def test_message_creation_missing_content_raises_error(self) -> None:
        """Test that creating a message without content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role=MessageRole.USER)
        
        assert "content" in str(exc_info.value).lower()

    def test_message_creation_empty_content_succeeds(self) -> None:
        """Test that messages can have empty content string."""
        message = Message(
            role=MessageRole.USER,
            content="",
        )

        assert message.content == ""


class TestMessageFormatting:
    """Test message formatting for display."""

    def test_message_format_for_display_user(self) -> None:
        """Test formatting a user message for display."""
        message = Message(
            role=MessageRole.USER,
            content="Hello!",
        )

        formatted = message.format_for_display()
        
        assert "User" in formatted
        assert "Hello!" in formatted
        assert message.timestamp.strftime("%H:%M") in formatted

    def test_message_format_for_display_assistant(self) -> None:
        """Test formatting an assistant message for display."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Hi there!",
        )

        formatted = message.format_for_display()
        
        assert "Assistant" in formatted
        assert "Hi there!" in formatted

    def test_message_format_for_display_system(self) -> None:
        """Test formatting a system message for display."""
        message = Message(
            role=MessageRole.SYSTEM,
            content="Connection established.",
        )

        formatted = message.format_for_display()
        
        assert "System" in formatted
        assert "Connection established." in formatted

    def test_message_format_with_custom_name(self) -> None:
        """Test formatting a message with custom persona name in metadata."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata={"persona_name": "Technical Expert"},
        )

        formatted = message.format_for_display()
        
        # Should use persona name if available
        assert "Technical Expert" in formatted or "Assistant" in formatted


class TestMessageSerialization:
    """Test message serialization to/from JSON."""

    def test_message_serialization_to_dict(self) -> None:
        """Test that a message can be serialized to a dictionary."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        message = Message(
            role=MessageRole.USER,
            content="Test message",
            timestamp=timestamp,
            metadata={"key": "value"},
        )

        message_dict = message.model_dump()

        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Test message"
        assert message_dict["metadata"] == {"key": "value"}

    def test_message_serialization_to_json(self) -> None:
        """Test that a message can be serialized to JSON string."""
        message = Message(
            role=MessageRole.USER,
            content="Test",
        )

        message_json = message.model_dump_json()
        parsed = json.loads(message_json)

        assert parsed["role"] == "user"
        assert parsed["content"] == "Test"

    def test_message_deserialization_from_dict(self) -> None:
        """Test that a message can be created from a dictionary."""
        data = {
            "role": "user",
            "content": "Test",
            "timestamp": "2024-01-01T12:00:00",
            "metadata": {},
        }

        message = Message.model_validate(data)

        assert message.role == MessageRole.USER
        assert message.content == "Test"

    def test_message_roundtrip_serialization(self) -> None:
        """Test that serialization and deserialization preserve data."""
        original = Message(
            role=MessageRole.ASSISTANT,
            content="Original message",
            metadata={"test": True},
        )

        # Dict roundtrip
        dict_data = original.model_dump()
        from_dict = Message.model_validate(dict_data)
        
        assert original.role == from_dict.role
        assert original.content == from_dict.content
        assert original.metadata == from_dict.metadata


class TestMessageRole:
    """Test MessageRole enum."""

    def test_message_role_enum_values(self) -> None:
        """Test that MessageRole enum has expected values."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"

    def test_message_role_from_string(self) -> None:
        """Test that MessageRole can be created from string."""
        message = Message(
            role="user",
            content="Test",
        )

        assert message.role == MessageRole.USER
