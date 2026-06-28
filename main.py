#!/usr/bin/env python3
"""small-claude-code CLI - Interactive agent harness."""

import os
import sys
from pathlib import Path

from small_claude_code import AgentLoop, Config
from small_claude_code.tools import (
    BashTool,
    ReadTool,
    WriteTool,
    EditTool,
    GlobTool,
    GrepTool,
)


def create_agent() -> AgentLoop:
    """Create and configure an agent with common tools."""
    config = Config.from_env()

    # Ensure API key is set
    if not config.api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it before running the agent.")
        sys.exit(1)

    # Ensure directories exist
    config.ensure_dirs()

    # Create agent
    agent = AgentLoop(config)

    # Register tools
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
    agent.register_tool("read", ReadTool(workdir=str(config.workdir)))
    agent.register_tool("write", WriteTool(workdir=str(config.workdir)))
    agent.register_tool("edit", EditTool(workdir=str(config.workdir)))
    agent.register_tool("glob", GlobTool(workdir=str(config.workdir)))
    agent.register_tool("grep", GrepTool(workdir=str(config.workdir)))

    return agent


def print_welcome():
    """Print welcome message."""
    print("=" * 60)
    print("small-claude-code - Agent Harness CLI")
    print("=" * 60)
    print("Type your message and press Enter to chat with the agent.")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'clear' to clear conversation history.")
    print("=" * 60)
    print()


def main():
    """Main entry point."""
    print_welcome()

    agent = create_agent()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            agent.clear_messages()
            print("Conversation cleared.")
            continue

        print("\nAgent: ", end="", flush=True)
        try:
            response = agent.run(user_input)
            print(response)
        except Exception as e:
            print(f"Error: {e}")

        print()


if __name__ == "__main__":
    main()