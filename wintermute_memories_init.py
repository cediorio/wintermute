#!/usr/bin/env python3
"""Import memories from wintermute_memories.json into OpenMemory."""

import asyncio
import json
import sys
import time
from pathlib import Path

import httpx


# Configuration
OPENMEMORY_URL = "http://localhost:8080/memory/add"
MEMORIES_FILE = "wintermute_memories.json"


def load_memories_from_json(file_path: str) -> list[dict]:
    """
    Load memories from JSON file.

    Expected format:
    [
        {
            "character_id": "default",
            "content": "User likes jazz music",
            "tags": ["preferences", "music"]
        },
        {
            "character_id": "technical",
            "content": "User prefers Python over JavaScript",
            "tags": ["preferences", "programming"]
        }
    ]

    Args:
        file_path: Path to the JSON file.

    Returns:
        List of memory dictionaries.
    """
    try:
        with open(file_path, "r") as f:
            memories = json.load(f)

        if not isinstance(memories, list):
            print(f"Error: {file_path} must contain a JSON array")
            sys.exit(1)

        return memories
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        print(f"\nCreate {file_path} with this format:")
        print(
            json.dumps(
                [
                    {
                        "character_id": "default",
                        "content": "Example memory content",
                        "tags": ["example", "test"],
                    }
                ],
                indent=2,
            )
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


async def add_memory(
    content: str, character_id: str, tags: list[str] | None = None
) -> tuple[bool, str]:
    """
    Add a memory to OpenMemory.

    Args:
        content: The memory content.
        character_id: The character ID (used as user_id).
        tags: Optional tags for the memory.

    Returns:
        Tuple of (success: bool, message: str)
    """
    payload = {
        "content": content,
        "user_id": character_id,
    }

    if tags:
        payload["tags"] = tags

    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENMEMORY_URL, json=payload, headers=headers)

            if response.status_code == 200:
                return True, "Success"
            else:
                return False, f"{response.status_code} - {response.text}"
    except Exception as e:
        return False, str(e)


async def main():
    """Import memories from JSON file."""
    print(f"Loading memories from {MEMORIES_FILE}...")
    memories = load_memories_from_json(MEMORIES_FILE)

    print(f"Found {len(memories)} memories to import\n")

    success_count = 0
    error_count = 0

    for i, memory in enumerate(memories, 1):
        # Validate memory structure
        if "content" not in memory:
            print(f"[{i}/{len(memories)}] Skipping - missing 'content' field")
            error_count += 1
            continue

        if "character_id" not in memory:
            print(f"[{i}/{len(memories)}] Skipping - missing 'character_id' field")
            error_count += 1
            continue

        content = memory["content"]
        character_id = memory["character_id"]
        tags = memory.get("tags", [])

        # Add to OpenMemory
        success, message = await add_memory(content, character_id, tags)

        if success:
            print(f"[{i}/{len(memories)}] ✅ Added to '{character_id}': {content[:60]}...")
            success_count += 1
        else:
            print(f"[{i}/{len(memories)}] ❌ Failed: {content[:60]}...")
            print(f"           Error: {message}")
            error_count += 1

        # Small delay to avoid overwhelming the server
        await asyncio.sleep(0.1)

    print(f"\n{'=' * 60}")
    print(f"Import complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    print(f"  Total:   {len(memories)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
