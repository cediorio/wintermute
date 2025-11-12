#!/usr/bin/env python3
"""Check status of Ollama and OpenMemory services."""

import asyncio

from wintermute.services.memory_client import MemoryClient
from wintermute.services.ollama_client import OllamaClient
from wintermute.utils.config import Config


async def check_services():
    """Check connection status of all services."""
    config = Config()
    
    print("🔍 Checking Service Connections...")
    print("=" * 60)
    
    # Check Ollama
    print(f"\n📡 Ollama: {config.ollama_url}")
    print(f"   Model: {config.ollama_model}")
    ollama = OllamaClient(config)
    ollama_ok = await ollama.check_connection()
    
    if ollama_ok:
        print("   ✅ Connected")
    else:
        print("   ❌ Not connected")
        print("   → Start Ollama: ollama serve")
    
    await ollama.close()
    
    # Check OpenMemory
    print(f"\n🧠 OpenMemory: {config.openmemory_url}")
    print(f"   User ID: {config.user_id}")
    memory = MemoryClient(config)
    memory_ok = await memory.check_connection()
    
    if memory_ok:
        print("   ✅ Connected")
        stats = await memory.get_stats()
        print(f"   📊 Total memories: {stats.get('total', 0)}")
    else:
        print("   ❌ Not connected")
        print("   → Check OPENMEMORY_SETUP.md for setup instructions")
        print("   → The app will work without memory (no context retention)")
    
    print("\n" + "=" * 60)
    
    if ollama_ok and memory_ok:
        print("✅ All services ready!")
    elif ollama_ok:
        print("⚠️  Ollama ready, OpenMemory unavailable (reduced functionality)")
    elif memory_ok:
        print("⚠️  OpenMemory ready, Ollama unavailable (can't chat)")
    else:
        print("❌ No services available - check configuration")
    
    print("\nTo start chatting, run: uv run wintermute")


if __name__ == "__main__":
    asyncio.run(check_services())
