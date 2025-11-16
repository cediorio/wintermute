# Wintermute - TUI Chatbot with Personality & Memory

A terminal-based chatbot interface built with Textual, featuring personality-driven conversations with persistent memory using Ollama and OpenMemory.

## Features

- **Split-pane TUI Interface**: Clean terminal UI with separate chat and control panes
- **Multiple Personas**: Switch between different AI personalities with unique traits
- **Persistent Memory**: Long-term conversation memory using OpenMemory
- **Local-First**: Runs entirely on your machine using Ollama
- **Test-Driven**: Built with TDD methodology for reliability

## Architecture

### UI Layout
```
┌─────────────────────────┬──────────────────┐
│                         │   Persona Panel  │
│                         │                  │
│      Chat Panel         │   [Active: Tech] │
│                         │   - Default      │
│   User: Hello!          │   - Technical    │
│   Bot: Hi there!        │   - Creative     │
│                         ├──────────────────┤
│                         │   Status Panel   │
│                         │                  │
│                         │   ● Connected    │
│                         │   Memory: 42     │
└─────────────────────────┴──────────────────┘
```

### Components

1. **Left Pane - Chat Interface**
   - Message display with scrollback
   - Input field for user messages
   - Typing indicators
   - Message history

2. **Right Upper Pane - Persona Selector**
   - List of available personas
   - Current active persona highlighted
   - Quick-switch functionality
   - Persona descriptions

3. **Right Lower Pane - Status Display**
   - Connection status (Ollama & OpenMemory)
   - Memory count
   - Current model info
   - Performance metrics

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Ollama installed and running locally
- OpenMemory instance (local or remote)

## Installation

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <repository-url>
cd wintermute
```

3. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start required services:
```bash
# Start Ollama (if not already running)
ollama serve

# Start OpenMemory (Docker)
docker run -p 8080:8080 caviraoss/openmemory
```

## Usage

Run the application:
```bash
uv run wintermute
```

Or activate venv and run directly:
```bash
source .venv/bin/activate
python -m wintermute.app
```

### Keyboard Shortcuts

- `Ctrl+C` - Exit application
- `Ctrl+P` - Open persona selector
- `Up/Down` - Navigate chat history
- `Tab` - Switch between panes
- `Escape` - Clear input

## Configuration

Edit `.env` file:

```env
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenMemory Configuration
OPENMEMORY_URL=http://localhost:8080
OPENMEMORY_API_KEY=your-key-here

# Application Settings
DEFAULT_PERSONA=technical
MAX_MEMORY_ITEMS=100
```

## Personas

Personas are defined in `personas/*.json`:

```json
{
  "name": "Technical Assistant",
  "id": "technical",
  "description": "Expert in programming and system design",
  "system_prompt": "You are a technical expert...",
  "temperature": 0.7,
  "traits": ["analytical", "precise", "helpful"]
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=wintermute

# Run specific test file
uv run pytest tests/test_ui/test_chat_pane.py

# Run in watch mode
uv run pytest-watch
```

### TDD Workflow

1. Write a failing test
2. Implement minimum code to pass
3. Refactor while keeping tests green
4. Repeat

See `AGENTS.md` for detailed development plan.

### Development Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests with coverage
uv run pytest --cov=wintermute --cov-report=html

# Linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/

# Run app in dev mode
uv run python -m wintermute.app
```

## Project Structure

```
wintermute/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .env.example
├── src/
│   └── wintermute/
│       ├── __init__.py
│       ├── app.py              # Main Textual app
│       ├── ui/                 # UI components
│       ├── models/             # Data models
│       ├── services/           # External service clients
│       └── utils/              # Utilities
├── tests/                      # Test suite
└── personas/                   # Persona definitions
```

## Project Status

- [x] Phase 1: Core Models & Services ✅
  - [x] Data Models (Persona, Message)
  - [x] Configuration Management
  - [x] Ollama Client
  - [x] OpenMemory Client (with SDK)
  - [x] Persona Manager
- [x] Phase 2: UI Components ✅
  - [x] StatusPane
  - [x] PersonaPane
  - [x] ChatPane
- [x] Phase 3: Integration (Basic) ✅
  - [x] Main app layout
  - [x] Service initialization
  - [x] Keyboard bindings
  - [ ] Message flow (Ollama + Memory integration)
  - [ ] Event handling
  - [ ] End-to-end tests
- [ ] Phase 4: Polish & Features

**Current Stats:**
- 174 tests passing
- 95% code coverage
- All core components built and tested
- UI renders correctly!

## Contributing

This project follows TDD principles. All new features should:
1. Have tests written first
2. Pass all existing tests
3. Maintain >80% code coverage

## License

MIT License

## Acknowledgments

- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Ollama](https://ollama.ai/) - Local LLM backend
- [OpenMemory](https://github.com/CaviraOSS/OpenMemory) - Memory system
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
