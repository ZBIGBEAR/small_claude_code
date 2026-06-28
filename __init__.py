"""small-claude-code - A lightweight agent harness framework.

A simple but complete agent harness framework inspired by Claude Code.
Built from 0 to 1 with all core modules for commercial use.

Core Modules:
- core: Agent loop, message handling, configuration
- tools: Bash, file operations, search, web fetch
- permission: Permission guard with allow/deny/approve rules
- hooks: Extension points around tool execution
- task: Task management with persistence
- context: Context compaction for long conversations
- memory: Persistent memory store
- skill: Skill loading system
- subagent: Parallel subagent execution

Quick Start:
    from small_claude_code import AgentLoop, Config
    from small_claude_code.tools import BashTool, ReadTool

    config = Config.from_env()
    agent = AgentLoop(config)
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
    agent.register_tool("read", ReadTool(workdir=str(config.workdir)))

    result = agent.run("Read the README file")
    print(result)
"""

__version__ = "1.0.0"
__author__ = "small-claude-code"

from .core import AgentLoop, Config, Message, MessageRole
from .tools import BashTool, ReadTool, WriteTool, EditTool, GlobTool, GrepTool, WebFetchTool

__all__ = [
    # Version
    "__version__",
    # Core
    "AgentLoop",
    "Config",
    "Message",
    "MessageRole",
    # Tools
    "BashTool",
    "ReadTool",
    "WriteTool",
    "EditTool",
    "GlobTool",
    "GrepTool",
    "WebFetchTool",
]


def create_agent(**kwargs) -> AgentLoop:
    """Create a configured agent with common tools.

    Args:
        **kwargs: Configuration overrides

    Returns:
        Configured AgentLoop instance
    """
    config = Config.from_env()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    agent = AgentLoop(config)

    # Register default tools
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
    agent.register_tool("read", ReadTool(workdir=str(config.workdir)))
    agent.register_tool("write", WriteTool(workdir=str(config.workdir)))
    agent.register_tool("edit", EditTool(workdir=str(config.workdir)))
    agent.register_tool("glob", GlobTool(workdir=str(config.workdir)))
    agent.register_tool("grep", GrepTool(workdir=str(config.workdir)))

    return agent
