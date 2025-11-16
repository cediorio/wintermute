# OpenMemory Setup Guide

## Option 1: Start OpenMemory Locally

If you want to run OpenMemory on your local machine:

### Update .env
```bash
OPENMEMORY_URL=http://localhost:8080
```

### Start with Podman/Docker
# Start with --build on first run
docker compose up -d --build

# Check if it's running
curl http://localhost:8080/health
```

### Verify it's running
```bash
curl http://localhost:8080/health
```

## Testing the Connection

Once OpenMemory is running, test from Wintermute:

```bash
uv run python -c "
from wintermute.utils.config import Config
from wintermute.services.memory_client import MemoryClient
import asyncio

async def test():
    config = Config()
    client = MemoryClient(config)
    connected = await client.check_connection()
    print(f'OpenMemory connected: {connected}')
    
    if connected:
        # Test storing a memory
        mem_id = await client.store('Test memory')
        print(f'Stored memory with ID: {mem_id}')
        
        # Test querying
        results = await client.query('test')
        print(f'Found {len(results)} memories')

asyncio.run(test())
"
```

## Troubleshooting

### Connection Refused
- Ensure OpenMemory is running: `docker ps | grep openmemory`
- Check the port: `curl http://localhost:8080/health`
- Verify firewall rules if host is remote

### Port Already in Use
```bash
# Find what's using port 8080
sudo lsof -i :8080

# Stop existing service or change OM_PORT in docker-compose
```

### Check OpenMemory Logs
```bash
docker compose logs -f openmemory
```

## Without OpenMemory

Wintermute works fine without OpenMemory! It just won't have:
- Long-term memory across sessions
- Contextual recall from past conversations
- Memory-based personalization

The chat will still work normally, just without persistent memory.
