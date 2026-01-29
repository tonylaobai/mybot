# Clawdbot-Python

Python version of Clawdbot - A multi-channel AI assistant gateway

## Overview

This is a Python implementation of the original Clawdbot (Node.js), designed to provide a multi-channel AI assistant gateway supporting WhatsApp, Telegram, Discord, and other communication platforms.

## Architecture

The Python version maintains the core architecture principles of the original:

- **Gateway Core**: Central component managing connections and coordination
- **Channel Layer**: Support for multiple communication platforms
- **Tool Chain**: Rich functionality for file operations, system commands, etc.
- **AI Engine**: Dialog management and intelligent responses
- **Data Layer**: Persistent storage and memory functions

## Features

- Multi-platform messaging support
- Dynamic tool loading and permission management
- Secure execution sandbox
- Skill-based extensibility
- Memory and session management
- FastAPI-based REST API
- SQLite-backed persistent storage
- Async/await support for high concurrency

## Installation

```bash
# Clone the repository
git clone https://github.com/tonylaobai/clawdbot-python.git
cd clawdbot-python

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root to configure API keys and settings:

```env
CLAWDBOT_OPENAI_API_KEY=your_openai_api_key
CLAWDBOT_ANTHROPIC_API_KEY=your_anthropic_api_key
CLAWDBOT_SERVER_HOST=0.0.0.0
CLAWDBOT_SERVER_PORT=8000
CLAWDBOT_LOG_LEVEL=INFO
```

## Usage

### Running the Application

```bash
python -m src.main
```

### Using the API

Once running, the API will be available at `http://localhost:8000`:

```bash
# Check system health
curl http://localhost:8000/api/v1/gateway/health

# List available tools
curl http://localhost:8000/api/v1/tools/list

# Execute a tool
curl -X POST http://localhost:8000/api/v1/tools/exec/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "echo hello world"}'
```

### Demo

Run the demonstration to see all features in action:

```bash
python demo.py
```

## Project Structure

```
clawdbot-python/
├── src/                    # Source code
│   ├── core/              # Core components (gateway, config)
│   ├── agents/            # AI agent management
│   ├── channels/          # Communication channel management
│   ├── tools/             # Tool system and registry
│   ├── memory/            # Memory and persistence system
│   ├── api/               # API endpoints
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Package configuration
├── README.md              # This file
├── FULL_README.md         # Extended documentation
├── demo.py                # Demonstration script
├── test_basic.py          # Basic functionality tests
└── setup_instructions.md  # Setup instructions
```

## Core Components

### Gateway
The central coordinator that manages communication between all components. It handles message routing, system orchestration, and lifecycle management.

### Channels
Abstraction layer for different communication platforms (WhatsApp, Telegram, Discord, etc.). Each channel implements a common interface for sending and receiving messages.

### Agents
AI agent management system that handles conversation logic, tool usage, and response generation.

### Tools
Extensible tool system that provides safe access to system functions like file operations, command execution, and web services.

### Memory
Persistent storage system using SQLite for maintaining conversation history, user preferences, and contextual information.

## API Endpoints

The system exposes a comprehensive API via FastAPI:

- `/api/v1/gateway/health` - System health status
- `/api/v1/gateway/status` - Detailed system status
- `/api/v1/tools/list` - List available tools
- `/api/v1/tools/{tool_name}/execute` - Execute a specific tool
- `/api/v1/agents/list` - List available agents
- `/api/v1/channels/list` - List available channels
- `/api/v1/memory/search` - Search memory entries
- `/api/v1/interactions/recent` - Get recent interactions

## Security

The system includes several security measures:

- Sandboxed execution environment
- Tool permission management
- Input validation and sanitization
- Rate limiting capabilities
- Secure credential handling

## Extending Clawdbot-Python

### Adding New Tools

To create a new tool, inherit from `BaseTool` and implement the required methods:

```python
from src.tools.registry import BaseTool

class MyNewTool(BaseTool):
    async def run(self, param1: str, param2: int) -> str:
        # Implementation here
        return "result"
```

### Adding New Channels

To add support for a new communication platform, implement the `BaseChannel` interface:

```python
from src.channels.manager import BaseChannel

class MyNewChannel(BaseChannel):
    async def start(self):
        # Initialization code
        pass
    
    async def send_message(self, recipient_id: str, message: str, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
        # Send message implementation
        pass
```

## Development

To contribute to Clawdbot-Python:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Running Tests

```bash
python test_basic.py
```

## License

MIT License - see the LICENSE file in the repository.

## Acknowledgments

- Based on the original Clawdbot Node.js implementation
- Powered by FastAPI, SQLite, and modern Python async libraries
- Inspired by multi-platform communication needs

## Roadmap

Future enhancements planned:

- Enhanced AI model integration
- More communication channels
- Advanced memory management
- Plugin system for extensions
- Web-based administration interface
- Improved security features
- Better error handling and recovery
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.