"""Ollama API client for LLM interactions."""

import json
from collections.abc import AsyncIterator

from httpx import AsyncClient, ConnectError, TimeoutException

from wintermute.utils.config import Config


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, config: Config) -> None:
        """
        Initialize the Ollama client.

        Args:
            config: Application configuration containing Ollama settings.
        """
        self.base_url = str(config.ollama_url).rstrip("/")
        self.model = config.ollama_model
        self._client = AsyncClient(base_url=self.base_url, timeout=30.0)

    async def check_connection(self) -> bool:
        """
        Check if the Ollama server is reachable.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except (ConnectError, TimeoutException, Exception):
            return False

    async def generate(
        self,
        prompt: str,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """
        Generate a response from Ollama for the given prompt.

        Args:
            prompt: The user prompt to generate a response for.
            temperature: Optional temperature parameter (0.0-2.0).
            system_prompt: Optional system prompt to set context.

        Returns:
            The generated response text.

        Raises:
            ConnectionError: If connection to Ollama fails.
            TimeoutError: If the request times out.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        # Add optional parameters
        if temperature is not None or system_prompt is not None:
            if temperature is not None:
                payload["options"] = {"temperature": temperature}
            if system_prompt is not None:
                payload["system"] = system_prompt

        try:
            response = await self._client.post("/api/generate", json=payload)
            if response.status_code >= 400:
                response.raise_for_status()
            data = response.json()
            return data["response"]
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}") from e
        except TimeoutException as e:
            raise TimeoutError(f"Request to Ollama timed out: {e}") from e

    async def stream(
        self,
        prompt: str,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream a response from Ollama for the given prompt.

        Args:
            prompt: The user prompt to generate a response for.
            temperature: Optional temperature parameter (0.0-2.0).
            system_prompt: Optional system prompt to set context.

        Yields:
            Response chunks as they arrive.

        Raises:
            ConnectionError: If connection to Ollama fails.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }

        if temperature is not None or system_prompt is not None:
            if temperature is not None:
                payload["options"] = {"temperature": temperature}
            if system_prompt is not None:
                payload["system"] = system_prompt

        try:
            async with self._client.stream("POST", "/api/generate", json=payload) as response:
                async for line in response.aiter_bytes():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data and not data.get("done", False):
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}") from e

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "OllamaClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
