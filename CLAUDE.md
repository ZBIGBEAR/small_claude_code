# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

small-claude-code is a lightweight agent harness framework inspired by Claude Code. It provides a complete agent loop with tool execution, permission guards, hooks, context management, memory, skills, and subagent support.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run examples
python examples/simple_agent.py        # Basic agent with bash, read, write tools
python examples/task_agent.py         # Task management example
python examples/permission_agent.py   # Permission guard example

# Run tests
pytest

# Run a specific test file
pytest tests/test_core.py -v
```

## Architecture

### Core Modules (`harness/core/`)
- **agent_loop.py**: Heart of the framework - sends messages to the model, handles tool use requests, manages conversation state
- **config.py**: Configuration dataclass with model settings, paths, permission defaults, loaded from environment variables
- **message.py**: Message and ContentBlock classes for conversation state, supports text/tool_use/tool_result blocks

### Tools (`harness/tools/`)
- **base.py**: BaseTool abstract class and ToolResult dataclass
- **bash.py**: BashTool - executes shell commands
- **file.py**: ReadTool, WriteTool, EditTool - file operations with workdir restriction
- **search.py**: GlobTool, GrepTool - file search operations
- **web.py**: WebFetchTool - HTTP requests

### Permission (`harness/permission/`)
- **guard.py**: PermissionGuard with AllowRule, DenyRule, ApproveRule for tool execution control
- Rules support glob patterns for bash commands and file paths
- Approval callback for interactive confirmation

### Other Modules
- **hooks/**: Extension points before/after tool execution
- **task/**: Task persistence and management
- **context/**: Context compaction for long conversations
- **memory/**: Persistent memory store
- **skill/**: Skill loading system from directory
- **subagent/**: Parallel subagent execution

## Key Patterns

### Creating an Agent
```python
from harness import AgentLoop, Config
from harness.tools import BashTool, ReadTool

config = Config.from_env()
agent = AgentLoop(config)
agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
agent.register_tool("read", ReadTool(workdir=str(config.workdir)))
result = agent.run("Your task here")
```

### Permission Guard Usage
```python
from harness.permission import PermissionGuard, AllowRule, DenyRule

guard = PermissionGuard()
guard.allow("bash", "ls *")           # Allow specific patterns
guard.deny("bash", "rm -rf *")        # Deny dangerous commands
guard.deny("write", "*.env")          # Deny editing env files
agent.register_hook(guard.wrap_tool)  # Apply to all tools
```

### Environment Variables
- `ANTHROPIC_API_KEY`: Anthropic API key (required)
- `ANTHROPIC_API_BASE`: API base URL (default: https://api.anthropic.com/v1)
- `CLAUDE_MODEL`: Model name (default: claude-sonnet-4-20250514)
- `CLAUDE_WORKDIR`: Working directory for file operations
- `CLAUDE_TASKS_DIR`: Task persistence directory
- `CLAUDE_MEMORY_DIR`: Memory store directory
- `CLAUDE_SKILLS_DIR`: Skills directory