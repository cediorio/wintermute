"""Tests for the OpenMemory client."""

import pytest

from wintermute.services.memory_client import MemoryClient
from wintermute.utils.config import Config


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration for testing."""
    return Config(
        _env_file=None,
        openmemory_url="http://test:8080",
        openmemory_api_key="test-key",
        user_id="test-user",
    )


@pytest.fixture
def memory_client(mock_config: Config) -> MemoryClient:
    """Create a MemoryClient instance for testing."""
    return MemoryClient(mock_config)


class TestMemoryClientInitialization:
    """Test MemoryClient initialization."""

    def test_client_initialization_with_config(self, mock_config: Config) -> None:
        """Test that client can be initialized with config."""
        client = MemoryClient(mock_config)

        assert client.base_url == str(mock_config.openmemory_url).rstrip("/")
        assert client.api_key == mock_config.openmemory_api_key
        assert client.user_id == mock_config.user_id

    def test_client_initialization_without_api_key(self) -> None:
        """Test that client can be initialized without API key."""
        config = Config(
            _env_file=None,
            openmemory_url="http://test:8080",
            openmemory_api_key=None,
        )
        client = MemoryClient(config)

        assert client.api_key is None

    def test_client_creates_openmemory_instance(
        self, memory_client: MemoryClient
    ) -> None:
        """Test that initialization creates an OpenMemory SDK instance."""
        assert memory_client._om is not None


class TestMemoryClientHealthCheck:
    """Test memory client health/connection checking."""

    async def test_check_connection_success(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test successful connection check."""
        mocker.patch.object(memory_client._om, "health", return_value={"status": "ok"})

        result = await memory_client.check_connection()

        assert result is True

    async def test_check_connection_failure(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test connection check fails on error."""
        mocker.patch.object(
            memory_client._om,
            "health",
            side_effect=Exception("Connection failed"),
        )

        result = await memory_client.check_connection()

        assert result is False


class TestMemoryClientStore:
    """Test storing memories."""

    async def test_store_simple_content(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test storing a simple memory."""
        mock_response = {"id": "mem_123", "content": "Test memory"}
        mock_add = mocker.patch.object(
            memory_client._om, "add", return_value=mock_response
        )

        memory_id = await memory_client.store("Test memory")

        assert memory_id == "mem_123"
        mock_add.assert_called_once()
        call_args = mock_add.call_args[0][0]
        assert call_args["content"] == "Test memory"
        assert call_args["user_id"] == "test-user"

    async def test_store_with_tags(self, memory_client: MemoryClient, mocker) -> None:
        """Test storing a memory with tags."""
        mock_response = {"id": "mem_456"}
        mock_add = mocker.patch.object(
            memory_client._om, "add", return_value=mock_response
        )

        memory_id = await memory_client.store(
            "Test memory", tags=["important", "conversation"]
        )

        assert memory_id == "mem_456"
        call_args = mock_add.call_args[0][0]
        assert call_args["tags"] == ["important", "conversation"]

    async def test_store_with_custom_user_id(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test storing a memory with custom user_id."""
        mock_response = {"id": "mem_789"}
        mock_add = mocker.patch.object(
            memory_client._om, "add", return_value=mock_response
        )

        memory_id = await memory_client.store("Test", user_id="custom-user")

        call_args = mock_add.call_args[0][0]
        assert call_args["user_id"] == "custom-user"

    async def test_store_handles_error(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test that store handles errors gracefully."""
        mocker.patch.object(
            memory_client._om, "add", side_effect=Exception("API Error")
        )

        with pytest.raises(Exception) as exc_info:
            await memory_client.store("Test")

        assert "API Error" in str(exc_info.value)


class TestMemoryClientQuery:
    """Test querying memories."""

    async def test_query_simple(self, memory_client: MemoryClient, mocker) -> None:
        """Test querying memories with simple text."""
        mock_response = {
            "items": [
                {"id": "mem_1", "content": "Memory 1", "score": 0.95},
                {"id": "mem_2", "content": "Memory 2", "score": 0.85},
            ]
        }
        mock_query = mocker.patch.object(
            memory_client._om, "query", return_value=mock_response
        )

        results = await memory_client.query("test query")

        assert len(results) == 2
        assert results[0]["content"] == "Memory 1"
        assert results[0]["score"] == 0.95
        mock_query.assert_called_once()

    async def test_query_with_limit(self, memory_client: MemoryClient, mocker) -> None:
        """Test querying with custom limit."""
        mock_response = {"items": []}
        mock_query = mocker.patch.object(
            memory_client._om, "query", return_value=mock_response
        )

        await memory_client.query("test", limit=5)

        call_args = mock_query.call_args[0][0]
        assert call_args["top_k"] == 5

    async def test_query_filters_by_user_id(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test that query filters by user_id."""
        mock_response = {"items": []}
        mock_query = mocker.patch.object(
            memory_client._om, "query", return_value=mock_response
        )

        await memory_client.query("test")

        call_args = mock_query.call_args[0][0]
        assert call_args["user_id"] == "test-user"

    async def test_query_with_custom_user_id(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test querying with custom user_id."""
        mock_response = {"items": []}
        mock_query = mocker.patch.object(
            memory_client._om, "query", return_value=mock_response
        )

        await memory_client.query("test", user_id="other-user")

        call_args = mock_query.call_args[0][0]
        assert call_args["user_id"] == "other-user"

    async def test_query_returns_empty_list_on_error(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test that query returns empty list on error."""
        mocker.patch.object(
            memory_client._om, "query", side_effect=Exception("Query failed")
        )

        results = await memory_client.query("test")

        assert results == []


class TestMemoryClientGetStats:
    """Test getting memory statistics."""

    async def test_get_stats_success(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test getting memory statistics."""
        mock_all = mocker.patch.object(
            memory_client._om, "all", return_value={"items": [1, 2, 3, 4, 5]}
        )

        stats = await memory_client.get_stats()

        assert stats["total"] == 5
        mock_all.assert_called_once()

    async def test_get_stats_handles_error(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test that get_stats handles errors gracefully."""
        mocker.patch.object(
            memory_client._om, "all", side_effect=Exception("Stats failed")
        )

        stats = await memory_client.get_stats()

        assert stats == {}


class TestMemoryClientDelete:
    """Test deleting memories."""

    async def test_delete_memory_by_id(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test deleting a memory by ID."""
        mock_delete = mocker.patch.object(
            memory_client._om, "delete", return_value={"success": True}
        )

        result = await memory_client.delete("mem_123")

        assert result is True
        mock_delete.assert_called_once_with("mem_123")

    async def test_delete_handles_error(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test that delete handles errors gracefully."""
        mocker.patch.object(
            memory_client._om, "delete", side_effect=Exception("Delete failed")
        )

        result = await memory_client.delete("mem_123")

        assert result is False


class TestMemoryClientGetUserSummary:
    """Test getting user summary."""

    async def test_get_user_summary_success(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test getting user summary."""
        mock_query = mocker.patch.object(
            memory_client._om,
            "query",
            return_value={
                "items": [
                    {"content": "User likes coffee", "score": 0.9},
                    {"content": "User works at night", "score": 0.8},
                ]
            },
        )

        summary = await memory_client.get_user_summary()

        assert "coffee" in summary.lower()
        assert "night" in summary.lower()
        mock_query.assert_called_once()

    async def test_get_user_summary_with_custom_user_id(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test getting summary for custom user_id."""
        mock_query = mocker.patch.object(
            memory_client._om, "query", return_value={"items": []}
        )

        await memory_client.get_user_summary(user_id="other-user")

        call_args = mock_query.call_args[0][0]
        assert call_args["user_id"] == "other-user"

    async def test_get_user_summary_empty_memories(
        self, memory_client: MemoryClient, mocker
    ) -> None:
        """Test getting summary when no memories exist."""
        mocker.patch.object(
            memory_client._om, "query", return_value={"items": []}
        )

        summary = await memory_client.get_user_summary()

        assert summary == "No memories found for this user."
