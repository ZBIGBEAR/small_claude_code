#!/usr/bin/env python3
"""Simple agent example.

This example demonstrates:
- Basic agent loop
- Tool registration
- Simple task execution
"""

from small_claude_code import AgentLoop, Config, BashTool, ReadTool, WriteTool


def main():
    # Create configuration
    config = Config.from_env()
    config.system_prompt = """You are a helpful coding assistant.
You have access to bash commands and file operations.
Always be careful with destructive operations."""

    # Create agent
    agent = AgentLoop(config)

    # Register tools
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
    agent.register_tool("read", ReadTool(workdir=str(config.workdir)))
    agent.register_tool("write", WriteTool(workdir=str(config.workdir)))

    # Run a simple task
    print("Running simple agent task...")
    result = agent.run(
        "List the files in the current directory using bash ls -la"
    )
    print("\nResult:")
    print(result)


if __name__ == "__main__":
    main()
