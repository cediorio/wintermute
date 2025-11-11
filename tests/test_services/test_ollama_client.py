"""Tests for the Ollama client."""

import pytest
from httpx import AsyncClient, ConnectError, Request, Response, TimeoutException

from wintermute.services.ollama_client import OllamaClient
from wintermute.utils.config import Config


def create_mock_response(status_code: int, json_data: dict) -> Response:
    """Helper to create a properly mocked Response object."""
    request = Request("POST", "http://test/api/generate")
    return Response(status_code, json=json_data, request=request)


@pytest.fixture
def mock_config() -> Config:
    """Create a mock configuration for testing."""
    return Config(
        _env_file=None,
        ollama_url="http://test:11434",
        ollama_model="test-model",
    )


@pytest.fixture
def ollama_client(mock_config: Config) -> OllamaClient:
    """Create an OllamaClient instance for testing."""
    return OllamaClient(mock_config)


class TestOllamaClientInitialization:
    """Test OllamaClient initialization."""

    def test_client_initialization_with_config(self, mock_config: Config) -> None:
        """Test that client can be initialized with config."""
        client = OllamaClient(mock_config)

        assert client.base_url == str(mock_config.ollama_url).rstrip("/")
        assert client.model == mock_config.ollama_model

    def test_client_initialization_creates_http_client(
        self, ollama_client: OllamaClient
    ) -> None:
        """Test that initialization creates an httpx client."""
        assert ollama_client._client is not None
        assert isinstance(ollama_client._client, AsyncClient)


class TestOllamaClientHealthCheck:
    """Test Ollama client health/connection checking."""

    @pytest.mark.asyncio
    async def test_check_connection_success(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test successful connection check."""
        mock_response = create_mock_response(200, {"status": "ok"})
        mocker.patch.object(
            ollama_client._client, "get", return_value=mock_response
        )

        result = await ollama_client.check_connection()

        assert result is True
        ollama_client._client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_connection_failure_connection_error(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test connection check fails on connection error."""
        mocker.patch.object(
            ollama_client._client,
            "get",
            side_effect=ConnectError("Connection refused"),
        )

        result = await ollama_client.check_connection()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_connection_failure_timeout(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test connection check fails on timeout."""
        mocker.patch.object(
            ollama_client._client, "get", side_effect=TimeoutException("Timeout")
        )

        result = await ollama_client.check_connection()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_connection_failure_status_code(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test connection check fails on bad status code."""
        mock_response = create_mock_response(500, {"error": "Server error"})
        mocker.patch.object(
            ollama_client._client, "get", return_value=mock_response
        )

        result = await ollama_client.check_connection()

        assert result is False


class TestOllamaClientGenerate:
    """Test Ollama client generate method."""

    @pytest.mark.asyncio
    async def test_generate_with_simple_prompt(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test generating a response from a simple prompt."""
        mock_response = create_mock_response(
            200, {"response": "Hello! How can I help you?"}
        )
        mocker.patch.object(
            ollama_client._client, "post", return_value=mock_response
        )

        response = await ollama_client.generate("Hello")

        assert response == "Hello! How can I help you?"
        ollama_client._client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_includes_model_in_request(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that generate includes model name in request."""
        mock_response = create_mock_response(200, {"response": "Test response"})
        mock_post = mocker.patch.object(
            ollama_client._client, "post", return_value=mock_response
        )

        await ollama_client.generate("Test prompt")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_generate_includes_prompt_in_request(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that generate includes prompt in request."""
        mock_response = create_mock_response(200, {"response": "Test"})
        mock_post = mocker.patch.object(
            ollama_client._client, "post", return_value=mock_response
        )

        await ollama_client.generate("Test prompt")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["prompt"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_generate_with_custom_temperature(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test generating with custom temperature parameter."""
        mock_response = create_mock_response(200, {"response": "Response"})
        mock_post = mocker.patch.object(
            ollama_client._client, "post", return_value=mock_response
        )

        await ollama_client.generate("Test", temperature=0.9)

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["options"]["temperature"] == 0.9

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test generating with a system prompt."""
        mock_response = create_mock_response(200, {"response": "Response"})
        mock_post = mocker.patch.object(
            ollama_client._client, "post", return_value=mock_response
        )

        await ollama_client.generate("Test", system_prompt="You are helpful")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["system"] == "You are helpful"

    @pytest.mark.asyncio
    async def test_generate_handles_connection_error(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that generate handles connection errors gracefully."""
        mocker.patch.object(
            ollama_client._client,
            "post",
            side_effect=ConnectError("Connection refused"),
        )

        with pytest.raises(ConnectionError) as exc_info:
            await ollama_client.generate("Test")

        assert "ollama" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_handles_timeout(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that generate handles timeouts gracefully."""
        mocker.patch.object(
            ollama_client._client, "post", side_effect=TimeoutException("Timeout")
        )

        with pytest.raises(TimeoutError) as exc_info:
            await ollama_client.generate("Test")

        assert "timeout" in str(exc_info.value).lower()


class TestOllamaClientStream:
    """Test Ollama client streaming responses."""

    @pytest.mark.asyncio
    async def test_stream_yields_response_chunks(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that stream yields response chunks."""
        mock_chunks = [
            b'{"response": "Hello"}\n',
            b'{"response": " there"}\n',
            b'{"response": "!"}\n',
            b'{"done": true}\n',
        ]

        async def mock_aiter_bytes():
            for chunk in mock_chunks:
                yield chunk

        mock_response = mocker.Mock()
        mock_response.aiter_bytes = mock_aiter_bytes
        
        mock_stream_context = mocker.Mock()
        mock_stream_context.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = mocker.AsyncMock(return_value=None)
        
        mocker.patch.object(
            ollama_client._client, "stream", return_value=mock_stream_context
        )

        chunks = []
        async for chunk in ollama_client.stream("Hello"):
            chunks.append(chunk)

        assert chunks == ["Hello", " there", "!"]

    @pytest.mark.asyncio
    async def test_stream_includes_model_and_prompt(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that stream includes model and prompt in request."""
        mock_chunks = [b'{"done": true}\n']

        async def mock_aiter_bytes():
            for chunk in mock_chunks:
                yield chunk

        mock_response = mocker.Mock()
        mock_response.aiter_bytes = mock_aiter_bytes
        
        mock_stream_context = mocker.Mock()
        mock_stream_context.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = mocker.AsyncMock(return_value=None)
        
        mock_stream = mocker.patch.object(
            ollama_client._client, "stream", return_value=mock_stream_context
        )

        async for _ in ollama_client.stream("Test prompt"):
            pass

        call_kwargs = mock_stream.call_args[1]
        assert call_kwargs["json"]["model"] == "test-model"
        assert call_kwargs["json"]["prompt"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_stream_with_custom_parameters(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test streaming with custom parameters."""
        mock_chunks = [b'{"done": true}\n']

        async def mock_aiter_bytes():
            for chunk in mock_chunks:
                yield chunk

        mock_response = mocker.Mock()
        mock_response.aiter_bytes = mock_aiter_bytes
        
        mock_stream_context = mocker.Mock()
        mock_stream_context.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = mocker.AsyncMock(return_value=None)
        
        mock_stream = mocker.patch.object(
            ollama_client._client, "stream", return_value=mock_stream_context
        )

        async for _ in ollama_client.stream(
            "Test", temperature=0.8, system_prompt="Be helpful"
        ):
            pass

        call_kwargs = mock_stream.call_args[1]
        assert call_kwargs["json"]["options"]["temperature"] == 0.8
        assert call_kwargs["json"]["system"] == "Be helpful"

    @pytest.mark.asyncio
    async def test_stream_handles_connection_error(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that stream handles connection errors gracefully."""
        mocker.patch.object(
            ollama_client._client,
            "stream",
            side_effect=ConnectError("Connection refused"),
        )

        with pytest.raises(ConnectionError):
            async for _ in ollama_client.stream("Test"):
                pass


class TestOllamaClientCleanup:
    """Test OllamaClient resource cleanup."""

    @pytest.mark.asyncio
    async def test_client_close_closes_http_client(
        self, ollama_client: OllamaClient, mocker
    ) -> None:
        """Test that close method closes the HTTP client."""
        mock_aclose = mocker.patch.object(ollama_client._client, "aclose")

        await ollama_client.close()

        mock_aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_config: Config) -> None:
        """Test that client can be used as async context manager."""
        async with OllamaClient(mock_config) as client:
            assert client._client is not None

        # Client should be closed after context
        # (We'll verify this by checking if the client is properly cleaned up)
