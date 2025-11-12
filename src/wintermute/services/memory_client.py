"""OpenMemory client for long-term memory storage and retrieval."""

from typing import Any, Optional

from openmemory import OpenMemory

from wintermute.utils.config import Config


class MemoryClient:
    """Client for interacting with OpenMemory API using the official SDK."""

    def __init__(self, config: Config) -> None:
        """
        Initialize the Memory client.

        Args:
            config: Application configuration containing OpenMemory settings.
        """
        self.base_url = str(config.openmemory_url).rstrip("/")
        self.api_key = config.openmemory_api_key
        self.user_id = config.user_id

        # Initialize OpenMemory SDK
        if self.api_key:
            self._om = OpenMemory(base_url=self.base_url, api_key=self.api_key)
        else:
            self._om = OpenMemory(base_url=self.base_url)

    async def check_connection(self) -> bool:
        """
        Check if the OpenMemory server is reachable.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Try to get health status as a check
            self._om.health()
            return True
        except Exception:
            return False

    async def store(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Store a memory in OpenMemory.

        Args:
            content: The content to store.
            tags: Optional tags for the memory.
            user_id: Optional user_id (defaults to config user_id).

        Returns:
            The ID of the stored memory.

        Raises:
            Exception: If storage fails.
        """
        response = self._om.add(
            content=content,
            tags=tags,
            user_id=user_id or self.user_id,
        )
        return str(response["id"])

    async def query(
        self,
        query_text: str,
        limit: int = 10,
        user_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query memories semantically.

        Args:
            query_text: The query text to search for.
            limit: Maximum number of results to return.
            user_id: Optional user_id to filter by (defaults to config user_id).

        Returns:
            List of matching memories with scores.
        """
        try:
            filters: dict[str, Any] = {"user_id": user_id or self.user_id}
            response = self._om.query(query=query_text, k=limit, filters=filters)
            memories: list[dict[str, Any]] = response.get("matches", [])
            return memories
        except Exception:
            return []

    async def get_stats(self) -> dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary containing memory statistics.
        """
        try:
            # Get all memories and compute stats
            result = self._om.all()
            return {"total": len(result.get("items", []))}
        except Exception:
            return {}

    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            self._om.delete(memory_id)
            return True
        except Exception:
            return False

    async def get_user_summary(self, user_id: Optional[str] = None) -> str:
        """
        Get a summary of memories for a user.

        Args:
            user_id: Optional user_id (defaults to config user_id).

        Returns:
            A text summary of the user's memories.
        """
        try:
            # Query for general user information
            filters: dict[str, Any] = {"user_id": user_id or self.user_id}
            response = self._om.query(
                query="user preferences habits information", k=10, filters=filters
            )
            items = response.get("matches", [])

            if not items:
                return "No memories found for this user."

            # Combine top memories into a summary
            summary_parts = [item["content"] for item in items[:5]]
            return " | ".join(summary_parts)
        except Exception:
            return "No memories found for this user."
