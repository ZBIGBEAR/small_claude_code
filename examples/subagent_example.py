#!/usr/bin/env python3
"""Subagent example - parallel task execution.

This example demonstrates:
- Spawning multiple subagents
- Parallel task execution
- Result collection
"""

from harness import AgentLoop, Config, BashTool
from harness.subagent import SubagentRunner


def main():
    # Create configuration
    config = Config.from_env()

    # Create subagent runner
    runner = SubagentRunner(config)

    # Define tasks for parallel execution
    tasks = [
        ("List Python files", "find . -name '*.py' -type f | wc -l"),
        ("Count directories", "find . -type d | wc -l"),
        ("Check git status", "git status --short 2>/dev/null || echo 'Not a git repo'"),
        ("List config files", "find . -name '*.json' -o -name '*.yaml' -o -name '*.yml' | head -10"),
    ]

    print("Running parallel subagents...")
    subagent_ids = []

    # Spawn subagents
    for title, command in tasks:
        subagent_id = runner.run_async(
            task=f"Execute this command and return the output: {command}",
            system_prompt=f"You are a task executor. Run the given command and return the result.",
        )
        subagent_ids.append((subagent_id, title))
        print(f"  Spawned: {title} ({subagent_id})")

    # Collect results
    import time

    print("\nCollecting results...")
    for subagent_id, title in subagent_ids:
        result = runner.get_result(subagent_id)
        while result is None:
            time.sleep(0.5)
            result = runner.get_result(subagent_id)

        print(f"\n{title}:")
        print(f"  Status: {result.status.value}")
        if result.result:
            print(f"  Result: {result.result[:200]}")
        if result.error:
            print(f"  Error: {result.error}")

    # Cleanup
    runner.shutdown()


if __name__ == "__main__":
    main()
