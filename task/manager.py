"""Task system for Claude Harness.

The task system provides:
- Task creation and tracking
- Task dependencies (blockedBy)
- Persistence to disk
- Status tracking
"""

import json
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A task in the system."""

    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    blocked_by: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    result: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            blocked_by=data.get("blocked_by", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            result=data.get("result", ""),
            error=data.get("error", ""),
        )


class TaskManager:
    """Manager for tasks with persistence."""

    def __init__(self, tasks_dir: str | Path | None = None):
        """Initialize the task manager.

        Args:
            tasks_dir: Directory for task persistence
        """
        self.tasks_dir = Path(tasks_dir or Path.home() / ".claude" / "tasks")
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: dict[str, Task] = {}
        self.lock = threading.Lock()
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load tasks from disk."""
        task_file = self.tasks_dir / "tasks.json"
        if task_file.exists():
            try:
                data = json.loads(task_file.read_text())
                self.tasks = {k: Task.from_dict(v) for k, v in data.items()}
            except Exception:
                pass

    def _save_tasks(self) -> None:
        """Save tasks to disk."""
        task_file = self.tasks_dir / "tasks.json"
        data = {k: v.to_dict() for k, v in self.tasks.items()}
        task_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def create_task(
        self,
        title: str,
        description: str = "",
        blocked_by: list[str] | None = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title
            description: Task description
            blocked_by: IDs of tasks this is blocked by

        Returns:
            Created task
        """
        task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.tasks)}"
        task = Task(
            id=task_id,
            title=title,
            description=description,
            blocked_by=blocked_by or [],
        )

        with self.lock:
            self.tasks[task_id] = task
            self._save_tasks()

        return task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None
        """
        return self.tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: TaskStatus | None = None,
        result: str | None = None,
        error: str | None = None,
    ) -> Task | None:
        """Update a task.

        Args:
            task_id: Task ID
            status: New status
            result: Task result
            error: Task error

        Returns:
            Updated task or None
        """
        with self.lock:
            if task_id not in self.tasks:
                return None

            task = self.tasks[task_id]
            if status:
                task.status = status
            if result is not None:
                task.result = result
            if error is not None:
                task.error = error
            task.updated_at = datetime.now().isoformat()

            self._save_tasks()
            return task

    def list_tasks(
        self,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        """List tasks.

        Args:
            status: Filter by status

        Returns:
            List of tasks
        """
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def get_ready_tasks(self) -> list[Task]:
        """Get tasks that are ready to run (not blocked).

        Returns:
            List of tasks with no pending dependencies
        """
        ready = []
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            # Check if all blocked_by tasks are completed
            all_done = all(
                self.tasks.get(blocked_id, Task(id=blocked_id, title="", status=TaskStatus.COMPLETED)).status
                == TaskStatus.COMPLETED
                for blocked_id in task.blocked_by
            )
            if all_done:
                ready.append(task)
        return ready

    def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted
        """
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                self._save_tasks()
                return True
            return False
