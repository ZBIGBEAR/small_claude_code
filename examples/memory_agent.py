#!/usr/bin/env python3
"""Memory-enabled agent example.

This example demonstrates:
- Persistent memory store
- Memory search and retrieval
- Context-aware responses
"""

from harness import AgentLoop, Config, BashTool, ReadTool
from harness.memory import MemoryStore


def main():
    # Create configuration
    config = Config.from_env()

    # Create memory store
    memory = MemoryStore(config.memory_dir)

    # Add some memories
    print("Adding memories...")
    memory.add(
        "User prefers Python over other languages",
        entry_type="preference",
        metadata={"source": "conversation"},
    )
    memory.add(
        "Project is a Python CLI tool for AI agents",
        entry_type="fact",
        metadata={"source": "context"},
    )
    memory.add(
        "Working directory is /Users/liyuping/Workspace",
        entry_type="context",
        metadata={"source": "system"},
    )

    # Get context
    print("\nGetting context for 'project'...")
    context = memory.get_context("project")
    print(f"Context: {context}")

    # Create agent with memory
    agent = AgentLoop(config)
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))

    # Add memory to system prompt
    agent.config.system_prompt = f"""You are a helpful AI assistant.
You have access to the user's memory:
{memory.get_context("user preferences project")}

Use this information to provide personalized responses."""

    # Run task
    print("\nRunning memory-aware task...")
    result = agent.run("What do you know about the user's project?")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
