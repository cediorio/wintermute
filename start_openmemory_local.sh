#!/bin/bash
# Start OpenMemory locally for testing

echo "🚀 Starting OpenMemory locally on port 8080..."
echo ""
echo "This will:"
echo "  - Run OpenMemory in Docker"
echo "  - Use synthetic embeddings (no external LLM needed)"
echo "  - Store data in Docker volume"
echo ""

# Update .env to use localhost
sed -i 's|OPENMEMORY_URL=http://sqwadebase:8080|OPENMEMORY_URL=http://localhost:8080|' .env
echo "✏️  Updated .env to use localhost:8080"

# Start docker compose
docker compose up -d openmemory

echo ""
echo "⏳ Waiting for OpenMemory to start..."
sleep 5

# Check health
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ OpenMemory is running!"
    echo ""
    echo "Run: uv run python check_services.py"
else
    echo "❌ OpenMemory failed to start"
    echo "Check logs: docker compose logs openmemory"
fi
