#!/usr/bin/env python3
"""Permission-based agent example.

This example demonstrates:
- Permission guard setup
- Allow/deny rules
- Approval workflow
"""

from harness import AgentLoop, Config, BashTool, ReadTool, WriteTool
from harness.permission import PermissionGuard, PermissionAction


def approval_callback(tool_name: str, params: dict) -> bool:
    """Callback for approval requests.

    Args:
        tool_name: Tool name
        params: Tool parameters

    Returns:
        True if approved
    """
    print(f"\n[Approval Request] {tool_name}({params})")
    response = input("Approve? [y/N]: ").strip().lower()
    return response == "y"


def main():
    # Create configuration
    config = Config.from_env()

    # Create permission guard
    guard = PermissionGuard()
    guard.set_approval_callback(approval_callback)

    # Configure permissions
    # Allow safe read operations
    guard.allow("read", "**/*")
    guard.allow("glob", "**/*")
    guard.allow("grep", "**/*")

    # Require approval for bash
    guard.approve("bash", "**/*")

    # Deny dangerous operations
    guard.deny("bash", "rm -rf /**", "Cannot delete root filesystem")
    guard.deny("bash", "rm -rf /", "Cannot delete root filesystem")

    # Create agent with permission guard
    agent = AgentLoop(config)

    # Wrap tools with permission guard
    bash_tool = BashTool(workdir=str(config.workdir))
    read_tool = ReadTool(workdir=str(config.workdir))

    def safe_bash(**kwargs):
        result = guard.check("bash", kwargs)
        if result.action == PermissionAction.DENY:
            return f"Permission denied: {result.reason}"
        return bash_tool.execute(**kwargs).content

    def safe_read(**kwargs):
        result = guard.check("read", kwargs)
        if result.action == PermissionAction.DENY:
            return f"Permission denied: {result.reason}"
        return read_tool.execute(**kwargs).content

    agent.register_tool("bash", safe_bash)
    agent.register_tool("read", safe_read)
    agent.register_tool("write", WriteTool(workdir=str(config.workdir)))

    # Run tasks
    print("Task 1: Safe read")
    result1 = agent.run("Read the README.md file if it exists")
    print(f"Result: {result1[:200]}...")

    print("\nTask 2: Bash (will require approval)")
    result2 = agent.run("List files with ls -la")
    print(f"Result: {result2[:200]}...")


if __name__ == "__main__":
    main()
