# OpenMemory Setup Guide

## Current Status

Your configuration points to: `http://sqwadebase:8080`

The app works without OpenMemory (gracefully degrades), but to get full memory functionality, you need to start the OpenMemory service on sqwadebase.

## Option 1: Start OpenMemory Locally

If you want to run OpenMemory on your local machine instead:

### Update .env
```bash
OPENMEMORY_URL=http://localhost:8080
```

### Start with Docker
```bash
# Clone OpenMemory repo
git clone https://github.com/CaviraOSS/OpenMemory.git
cd OpenMemory

# Start with docker compose
docker compose up -d

# Check if it's running
curl http://localhost:8080/health
```

## Option 2: Start OpenMemory on sqwadebase

If sqwadebase is a remote server:

### SSH to sqwadebase
```bash
ssh sqwadebase
```

### Install and start OpenMemory
```bash
# Clone the repo
git clone https://github.com/CaviraOSS/OpenMemory.git
cd OpenMemory

# Start with docker compose
docker compose up -d

# Or run with Node.js
cd backend
npm install
npm run dev
```

### Verify it's running
```bash
curl http://localhost:8080/health
```

## Option 3: Use Synthetic Embeddings (Simplest)

The docker-compose.yml included in this repo is configured to use synthetic embeddings (no external LLM needed for embeddings):

```bash
# From wintermute directory
docker compose up -d openmemory

# Check logs
docker compose logs -f openmemory

# Check if it's running
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

## OpenMemory Configuration

The app uses these settings from `.env`:

```env
OPENMEMORY_URL=http://sqwadebase:8080  # Change to localhost:8080 if running locally
OPENMEMORY_API_KEY=                     # Leave empty for no auth
USER_ID=default_user                    # All your memories tagged with this
MAX_MEMORY_ITEMS=10000                  # Max memories to retrieve
```

## Troubleshooting

### Connection Refused
- Ensure OpenMemory is running: `docker ps | grep openmemory`
- Check the port: `curl http://sqwadebase:8080/health`
- Verify firewall rules if sqwadebase is remote

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
