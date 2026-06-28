# small-claude-code

A lightweight Agent Harness framework inspired by Claude Code. Built from 0 to 1 with all core modules for commercial use.

## Features

- **Core Modules**: Agent loop, message handling, configuration
- **Tools**: Bash, file operations, search, web fetch
- **Permission Guard**: Allow/Deny/Approve rules for tool execution control
- **Hooks**: Extension points before/after tool execution
- **Task Management**: Persistent task management
- **Context Compaction**: Context management for long conversations
- **Memory System**: Persistent memory store
- **Skill System**: Skill loading from directory
- **Subagent**: Parallel subagent execution

## Quick Start

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
pip install pytest  # Optional, for running tests

# Run examples
python examples/simple_agent.py        # Basic agent example
python examples/task_agent.py          # Task management example
python examples/permission_agent.py    # Permission guard example
python examples/memory_agent.py        # Memory system example
python examples/subagent_example.py    # Subagent example

# Run tests
pytest

# Run a specific test file
pytest tests/test_core.py -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) | - |
| `ANTHROPIC_API_BASE` | API base URL | `https://api.anthropic.com/v1` |
| `CLAUDE_MODEL` | Model name | `claude-sonnet-4-20250514` |
| `CLAUDE_WORKDIR` | Working directory for file operations | Current directory |
| `CLAUDE_TASKS_DIR` | Task persistence directory | `.tasks` |
| `CLAUDE_MEMORY_DIR` | Memory store directory | `.memory` |
| `CLAUDE_SKILLS_DIR` | Skills directory | `.skills` |

## Usage Examples

### Creating an Agent

```python
from small_claude_code import AgentLoop, Config
from small_claude_code.tools import BashTool, ReadTool

config = Config.from_env()
agent = AgentLoop(config)
agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
agent.register_tool("read", ReadTool(workdir=str(config.workdir)))

result = agent.run("Read the README file")
print(result)
```

### Using Permission Guard

```python
from small_claude_code.permission import PermissionGuard, PermissionAction

guard = PermissionGuard()
guard.allow("bash", "ls *")           # Allow specific patterns
guard.deny("bash", "rm -rf *")        # Deny dangerous commands
guard.deny("write", "*.env")          # Deny editing env files

# Wrap individual tools
bash_tool = BashTool(workdir=str(config.workdir))

def safe_bash(**kwargs):
    result = guard.check("bash", kwargs)
    if result.action == PermissionAction.DENY:
        return f"Permission denied: {result.reason}"
    return bash_tool.execute(**kwargs).content

agent.register_tool("bash", safe_bash)
```

## Project Structure

```
small_claude_code/
├── core/           # Core modules: agent loop, config, message
├── tools/          # Tools: bash, file, search, web
├── permission/     # Permission guard
├── hooks/          # Hook system
├── task/           # Task management
├── context/        # Context compaction
├── memory/         # Memory store
├── skill/          # Skill loader
├── subagent/       # Subagent execution
├── examples/       # Example code
└── tests/          # Tests
```

## License

MIT License