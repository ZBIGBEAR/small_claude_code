#!/usr/bin/env python3
"""Task-based agent example.

This example demonstrates:
- Task creation and tracking
- Task dependencies
- Persistent task management
"""

from harness import AgentLoop, Config, BashTool, ReadTool
from harness.task import TaskManager, TaskStatus


def main():
    # Create configuration
    config = Config.from_env()
    config.tasks_dir.mkdir(parents=True, exist_ok=True)

    # Create task manager
    task_manager = TaskManager(config.tasks_dir)

    # Create tasks
    print("Creating tasks...")
    task1 = task_manager.create_task(
        title="Explore project structure",
        description="List all Python files in the project",
    )
    task2 = task_manager.create_task(
        title="Analyze code",
        description="Count lines of code in Python files",
        blocked_by=[task1.id],
    )
    task3 = task_manager.create_task(
        title="Generate report",
        description="Create a summary report",
        blocked_by=[task2.id],
    )

    print(f"Created: {task1.id}, {task2.id}, {task3.id}")

    # Create agent
    agent = AgentLoop(config)
    agent.register_tool("bash", BashTool(workdir=str(config.workdir)))

    # Execute ready tasks
    print("\nExecuting ready tasks...")
    ready_tasks = task_manager.get_ready_tasks()
    for task in ready_tasks:
        print(f"\nWorking on: {task.title}")
        task_manager.update_task(task.id, TaskStatus.IN_PROGRESS)

        # Execute task
        if "Explore" in task.title:
            result = agent.run("Run: find . -name '*.py' -type f | head -20")
        else:
            result = agent.run(f"Task: {task.description}")

        task_manager.update_task(task.id, TaskStatus.COMPLETED, result=result)

    # Show all tasks
    print("\n\nAll tasks:")
    for task in task_manager.list_tasks():
        print(f"  [{task.status.value}] {task.title}")


if __name__ == "__main__":
    main()
