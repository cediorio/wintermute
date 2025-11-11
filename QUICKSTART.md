# Wintermute Quick Start Guide

## Initial Setup Complete! ✓

Your project structure has been created and is ready for development.

## What's Been Created

```
wintermute/
├── README.md              # Project overview and documentation
├── AGENTS.md              # TDD development plan
├── QUICKSTART.md          # This file
├── pyproject.toml         # Project configuration (uv-ready)
├── .env.example           # Configuration template
├── .gitignore             # Git ignore patterns
│
├── src/wintermute/        # Main source code
│   ├── __init__.py
│   ├── ui/                # UI components (to be built)
│   ├── models/            # Data models (to be built)
│   ├── services/          # External service clients (to be built)
│   └── utils/             # Utilities (to be built)
│
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_ui/           # UI component tests
│   ├── test_models/       # Model tests
│   ├── test_services/     # Service tests
│   ├── test_utils/        # Utility tests
│   └── test_integration/  # Integration tests
│
└── personas/              # AI persona definitions
    ├── default.json       # Default assistant
    ├── technical.json     # Technical expert
    └── creative.json      # Creative companion
```

## Next Steps

### 1. Install Dependencies

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project with dev dependencies
uv pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# - Update OLLAMA_URL if not using default
# - Set OPENMEMORY_API_KEY if required
# - Choose your DEFAULT_PERSONA
```

### 3. Start External Services

#### Ollama (LLM Backend)
```bash
# If not already installed, visit: https://ollama.ai
ollama serve

# Pull a model
ollama pull llama2
```

#### OpenMemory (Memory System)
```bash
# Using Docker
docker run -d -p 8080:8080 caviraoss/openmemory

# Or clone and run locally
git clone https://github.com/CaviraOSS/OpenMemory.git
cd OpenMemory/backend
npm install
npm run dev
```

### 4. Begin TDD Development

Follow the plan in `AGENTS.md`. Start with Phase 1:

#### Phase 1.1: Data Models

```bash
# Create your first test
touch tests/test_models/test_persona.py

# Write the test (following AGENTS.md)
# Run the test (it should fail - RED)
uv run pytest tests/test_models/test_persona.py -v

# Implement the model
touch src/wintermute/models/persona.py

# Make the test pass (GREEN)
uv run pytest tests/test_models/test_persona.py -v

# Refactor and repeat
```

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_models/test_persona.py

# With coverage
uv run pytest --cov=wintermute --cov-report=html

# Watch mode (runs tests on file changes)
uv run pytest-watch
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy src/
```

### Running the App (Once Built)

```bash
# Using uv run
uv run wintermute

# Or with activated venv
python -m wintermute.app
```

## TDD Development Process

For each feature in `AGENTS.md`:

1. **RED** - Write a failing test
   - Define expected behavior
   - Run test (should fail)

2. **GREEN** - Write minimal code to pass
   - Implement just enough to make test pass
   - Keep it simple

3. **REFACTOR** - Improve code quality
   - Clean up implementation
   - Tests should still pass
   - No new functionality

4. **COMMIT** - Save your progress
   ```bash
   git add .
   git commit -m "feat: implement persona model (TDD)"
   ```

## Recommended Development Order

Follow the sprints outlined in `AGENTS.md`:

### Sprint 1 (Week 1): Foundation
- [ ] Models: Persona, Message
- [ ] Utils: Config
- [ ] Basic test fixtures

### Sprint 2 (Week 2): Services
- [ ] OllamaClient
- [ ] MemoryClient
- [ ] PersonaManager

### Sprint 3 (Week 3): UI
- [ ] StatusPane
- [ ] PersonaPane
- [ ] ChatPane

### Sprint 4 (Week 4): Integration
- [ ] Main app
- [ ] Message flow
- [ ] End-to-end tests

### Sprint 5 (Week 5): Polish
- [ ] Advanced features
- [ ] Performance optimization
- [ ] Documentation

## Useful Resources

- **Textual Docs**: https://textual.textualize.io/
- **Ollama API**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **OpenMemory API**: https://openmemory.cavira.app/
- **Pytest Guide**: https://docs.pytest.org/
- **uv Documentation**: https://github.com/astral-sh/uv

## Troubleshooting

### Import errors during development
This is normal! Install dependencies first:
```bash
uv pip install -e ".[dev]"
```

### Ollama connection failed
- Ensure Ollama is running: `ollama serve`
- Check URL in `.env`: `OLLAMA_URL=http://localhost:11434`
- Test manually: `curl http://localhost:11434/api/tags`

### OpenMemory connection failed
- Ensure OpenMemory is running
- Check URL in `.env`: `OPENMEMORY_URL=http://localhost:8080`
- Test manually: `curl http://localhost:8080/health`

### Tests not found
- Ensure pytest can find tests: `uv run pytest --collect-only`
- Check pythonpath in `pyproject.toml`

## Getting Help

- Check `AGENTS.md` for detailed implementation guidance
- Review `README.md` for architecture overview
- Look at persona JSON files for examples

---

**Ready to start?** Begin with Phase 1.1 in `AGENTS.md` and write your first test! 🚀
