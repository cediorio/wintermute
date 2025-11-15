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
        if not user_id:
            raise ValueError("user_id (character_id) is required for storing memories")

        response = self._om.add(
            content=content,
            tags=tags,
            user_id=user_id,
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
            user_id: User ID (character ID) to filter by - REQUIRED.

        Returns:
            List of matching memories with scores.
        """
        try:
            if not user_id:
                return []

            filters: dict[str, Any] = {"user_id": user_id}
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

    async def get_all_for_user(self, user_id: str) -> list[dict[str, Any]]:
        """
        Get ALL memories for a specific user/character.

        Args:
            user_id: The user/character ID to get memories for.

        Returns:
            List of all memory objects for this user.
        """
        try:
            # Query with high limit to get all memories
            # Note: OpenMemory doesn't have a direct "get all" API,
            # so we use query with a very generic search
            filters: dict[str, Any] = {"user_id": user_id}
            response = self._om.query(
                query="",  # Empty query to match everything
                k=1000,  # High limit to get all
                filters=filters,
            )
            return response.get("matches", [])
        except Exception:
            return []

    async def get_user_summary(self, user_id: Optional[str] = None) -> str:
        """
        Get a summary of memories for a user.

        Args:
            user_id: Optional user_id (defaults to config user_id).

        Returns:
            A text summary of the user's memories.
        """
        try:
            if not user_id:
                return "No memories found for this user."

            # Query for general user information
            filters: dict[str, Any] = {"user_id": user_id}
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
