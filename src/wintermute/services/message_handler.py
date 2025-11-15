"""Message handler for coordinating chat flow between services."""

from typing import AsyncIterator

from wintermute.models.message import Message, MessageRole
from wintermute.models.character import Character
from wintermute.services.memory_client import MemoryClient
from wintermute.services.ollama_client import OllamaClient


class MessageHandler:
    """Handles message flow: retrieve context, generate response, store memory."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        memory_client: MemoryClient,
        global_system_prompt: str,
    ):
        """
        Initialize the MessageHandler.

        Args:
            ollama_client: Client for Ollama API.
            memory_client: Client for OpenMemory API.
            global_system_prompt: Global prompt prepended to all character prompts.
        """
        self.ollama = ollama_client
        self.memory = memory_client
        self.global_system_prompt = global_system_prompt

    async def process_message(
        self,
        user_message: str,
        character: Character,
        conversation_history: list[Message],
    ) -> str:
        """
        Process a user message and generate a response.

        Args:
            user_message: The user's input message.
            character: The active character to use for response generation.
            conversation_history: Recent conversation messages for context.

        Returns:
            The generated response text.
        """
        # 1. Query relevant memories for context
        memories = await self.memory.query(user_message, limit=5, user_id=character.id)

        # 2. Build context from memories
        memory_context = self._build_memory_context(memories)

        # 3. Build conversation context
        conversation_context = self._build_conversation_context(conversation_history)

        # 4. Build full prompt with character + context
        full_prompt = self._build_prompt(user_message, memory_context, conversation_context)

        # 5. Generate response from Ollama with combined system prompt
        combined_system_prompt = f"{self.global_system_prompt}\n\n{character.system_prompt}"
        response = await self.ollama.generate(
            full_prompt,
            temperature=character.temperature,
            system_prompt=combined_system_prompt,
        )

        # 6. Store conversation in memory
        await self._store_conversation(user_message, response, character.id)

        return response

    async def process_message_streaming(
        self,
        user_message: str,
        character: Character,
        conversation_history: list[Message],
    ) -> AsyncIterator[str]:
        """
        Process a user message and stream the response.

        Args:
            user_message: The user's input message.
            character: The active character to use for response generation.
            conversation_history: Recent conversation messages for context.

        Yields:
            Response text chunks as they arrive.
        """
        # 1. Query memories and build context
        memories = await self.memory.query(user_message, limit=5, user_id=character.id)
        memory_context = self._build_memory_context(memories)
        conversation_context = self._build_conversation_context(conversation_history)

        # 2. Build full prompt
        full_prompt = self._build_prompt(user_message, memory_context, conversation_context)

        # 3. Stream response from Ollama with combined system prompt
        combined_system_prompt = f"{self.global_system_prompt}\n\n{character.system_prompt}"
        full_response = ""
        async for chunk in self.ollama.stream(
            full_prompt,
            temperature=character.temperature,
            system_prompt=combined_system_prompt,
        ):
            full_response += chunk
            yield chunk

        # 4. Store complete conversation in memory
        await self._store_conversation(user_message, full_response, character.id)

    def _build_memory_context(self, memories: list[dict]) -> str:
        """
        Build context string from retrieved memories.

        Args:
            memories: List of memory items with content and scores.

        Returns:
            Formatted context string.
        """
        if not memories:
            return ""

        context_parts = [f"- {mem['content']}" for mem in memories[:3]]  # Top 3 most relevant
        return "Relevant context:\n" + "\n".join(context_parts)

    def _build_conversation_context(self, conversation_history: list[Message]) -> str:
        """
        Build context from recent conversation.

        Args:
            conversation_history: Recent messages in the conversation.

        Returns:
            Formatted conversation context.
        """
        if not conversation_history:
            return ""

        # Take last 5 messages for context
        recent = conversation_history[-5:]
        context_parts = []

        for msg in recent:
            role = msg.role.value.capitalize()
            context_parts.append(f"{role}: {msg.content}")

        return "Recent conversation:\n" + "\n".join(context_parts)

    def _build_prompt(
        self,
        user_message: str,
        memory_context: str,
        conversation_context: str,
    ) -> str:
        """
        Build the complete prompt for Ollama.

        Args:
            user_message: The user's current message.
            memory_context: Context from memories.
            conversation_context: Context from recent conversation.

        Returns:
            Complete prompt string.
        """
        parts = []

        if memory_context:
            parts.append(memory_context)

        if conversation_context:
            parts.append(conversation_context)

        parts.append(f"User: {user_message}")

        return "\n\n".join(parts)

    async def _store_conversation(
        self, user_message: str, assistant_response: str, character_id: str
    ) -> None:
        """
        Store the conversation in memory.

        Args:
            user_message: The user's message.
            assistant_response: The assistant's response.
        """
        try:
            # Store user message
            await self.memory.store(
                f"User said: {user_message}",
                tags=["conversation", "user"],
                user_id=character_id,
            )

            # Store assistant response
            await self.memory.store(
                f"Assistant replied: {assistant_response}",
                tags=["conversation", "assistant"],
                user_id=character_id,
            )
        except Exception as e:
            # Log error but don't fail the conversation
            import sys

            print(f"⚠️  Memory storage failed: {type(e).__name__}: {e}", file=sys.stderr)
