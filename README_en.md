# small-claude-code

> A lightweight agent harness framework - Build your own coding agent from scratch.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

## Overview

small-claude-code is a simple but complete agent harness framework inspired by Claude Code. It teaches how to build the "vehicle" around an AI model - the tools, knowledge, context management, and permissions that let an agent operate effectively.

**Agent = Model + Harness**

The model provides intelligence. The harness provides capability. This project focuses entirely on building the harness.

## Core Philosophy

> "Agency -- the capacity to perceive, reason, and act -- comes from model training, not from external code orchestration. But a working agent product needs both the model and the harness."

small-claude-code strips away complexity to teach the essential patterns:
- One agent loop
- Tool registration
- Permission boundaries
- Hook extension points
- Task persistence
- Context management
- Memory storage
- Skill loading
- Subagent coordination

## Features

| Module | Description |
|--------|-------------|
| **core** | Agent loop, message handling, configuration |
| **tools** | Bash, file operations, search, web fetch |
| **permission** | Allow/deny rules, approval workflow |
| **hooks** | Pre/post tool execution hooks |
| **task** | Task management with dependencies |
| **context** | Context compaction for long sessions |
| **memory** | Persistent cross-session memory |
| **skill** | Modular skill loading system |
| **subagent** | Parallel subagent execution |

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

```bash
export ANTHROPIC_API_KEY="your-api-key"
export CLAUDE_MODEL="claude-sonnet-4-20250514"  # Optional
export CLAUDE_WORKDIR="/path/to/workdir"        # Optional
```

### Simple Agent

```python
from harness import AgentLoop, Config, BashTool, ReadTool

# Create configuration
config = Config.from_env()
config.system_prompt = "You are a helpful coding assistant."

# Create agent
agent = AgentLoop(config)

# Register tools
agent.register_tool("bash", BashTool())
agent.register_tool("read", ReadTool())

# Run a task
result = agent.run("List files in the current directory")
print(result)
```

### With Permission Guard

```python
from harness import AgentLoop, Config, BashTool
from harness.permission import PermissionGuard, PermissionAction

guard = PermissionGuard()
guard.allow("read", "**/*")        # Allow all reads
guard.approve("bash", "**/*")      # Require approval for bash
guard.deny("bash", "rm -rf /**")  # Never allow destructive commands

# Wrap tools with permission guard
def safe_bash(**kwargs):
    result = guard.check("bash", kwargs)
    if result.action == PermissionAction.DENY:
        return f"Denied: {result.reason}"
    return bash_tool.execute(**kwargs).content

agent.register_tool("bash", safe_bash)
```

### With Task Management

```python
from harness.task import TaskManager, TaskStatus

task_manager = TaskManager()

# Create tasks with dependencies
task1 = task_manager.create_task(title="Explore project")
task2 = task_manager.create_task(
    title="Analyze code",
    blocked_by=[task1.id]
)

# Execute ready tasks
for task in task_manager.get_ready_tasks():
    task_manager.update_task(task.id, TaskStatus.IN_PROGRESS)
    result = agent.run(task.description)
    task_manager.update_task(task.id, TaskStatus.COMPLETED, result=result)
```

## Project Structure

```
small-claude-code/
├── harness/
│   ├── core/           # Agent loop and message handling
│   ├── tools/          # Tool implementations
│   ├── permission/     # Permission guard
│   ├── hooks/          # Hook system
│   ├── task/           # Task management
│   ├── context/        # Context compaction
│   ├── memory/         # Memory store
│   ├── skill/          # Skill loader
│   └── subagent/       # Subagent runner
├── examples/           # Example agents
└── tests/              # Unit tests
```

## Architecture

```
                    THE AGENT PATTERN
                    =================

    User --> messages[] --> LLM --> response
                                      |
                            stop_reason == "tool_use"?
                           /                          \
                         yes                           no
                          |                             |
                    execute tools                  return text
                    append results
                    loop back -----------------> messages[]


    The model decides when to call tools and when to stop.
    The harness just executes what the model asks for.
```

## Examples

| Example | Description |
|---------|-------------|
| `simple_agent.py` | Basic agent with tools |
| `task_agent.py` | Task management and tracking |
| `permission_agent.py` | Permission guard setup |
| `memory_agent.py` | Persistent memory |
| `subagent_example.py` | Parallel subagents |

## Running Examples

```bash
# Set up environment
export ANTHROPIC_API_KEY="your-key"

# Run simple agent
python examples/simple_agent.py

# Run with task management
python examples/task_agent.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Comparison with learn-claude-code

This project is a **simplified commercial version** of [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code):

| Aspect | learn-claude-code | small-claude-code |
|--------|------------------|----------------|
| Purpose | Educational/tutorial | Production-ready |
| Lessons | 20 progressive chapters | Core modules only |
| Complexity | Learning-focused | Simplified, clean |
| Documentation | Extensive | Focused on API |
| Structure | Teaching modules | Package structure |

## Commercial Use

small-claude-code is designed for commercial use:

- **MIT License** - Use freely in commercial projects
- **Minimal Dependencies** - Only requires `anthropic` SDK
- **Modular Design** - Use only what you need
- **Well-Tested** - Unit tests for all core modules
- **Documented** - Clear docstrings and examples

## Extending the Harness

### Adding Custom Tools

```python
from harness.tools.base import BaseTool, ToolResult

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"

    def execute(self, param: str) -> ToolResult:
        # Your implementation
        return ToolResult(success=True, content=f"Result: {param}")

agent.register_tool("my_tool", MyTool())
```

### Adding Hooks

```python
from harness.hooks import HookManager, HookType

def log_pre_tool(tool_name, params):
    print(f"Executing {tool_name}")

def log_post_tool(tool_name, result):
    print(f"Completed {tool_name}")

hooks = HookManager()
hooks.pre_tool("logger", log_pre_tool)
hooks.post_tool("logger", log_post_tool)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) - "Bash is all you need."

---

**Build the harness well. The model will do the rest.**
