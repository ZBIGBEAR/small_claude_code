"""Subagent runner for small-claude-code.

Subagents allow parallel task execution:
- Spawn isolated agent loops
- Return results to parent agent
- Independent tool sets
"""

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from ..core.agent_loop import AgentLoop
from ..core.config import Config
from ..core.message import Message


class SubagentStatus(str, Enum):
    """Subagent status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SubagentResult:
    """Result from a subagent."""

    id: str
    status: SubagentStatus
    result: str = ""
    error: str = ""
    duration: float = 0.0


class SubagentRunner:
    """Runner for parallel subagent execution."""

    def __init__(self, config: Config | None = None):
        """Initialize the subagent runner.

        Args:
            config: Configuration for subagents
        """
        self.config = config or Config.from_env()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.active_subagents: dict[str, Future] = {}
        self.results: dict[str, SubagentResult] = {}

    def run_async(
        self,
        task: str,
        tools: dict[str, Callable] | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 50,
    ) -> str:
        """Run a subagent task asynchronously.

        Args:
            task: Task description
            tools: Tool handlers
            system_prompt: Override system prompt
            max_iterations: Max iterations

        Returns:
            Subagent ID for tracking
        """
        subagent_id = f"sub-{uuid.uuid4().hex[:8]}"

        config = Config.from_env()
        if system_prompt:
            config.system_prompt = system_prompt

        def run():
            try:
                agent = AgentLoop(config)
                if tools:
                    for name, handler in tools.items():
                        agent.register_tool(name, handler)
                result = agent.run(task, max_iterations=max_iterations)
                self.results[subagent_id] = SubagentResult(
                    id=subagent_id,
                    status=SubagentStatus.COMPLETED,
                    result=result,
                )
            except Exception as e:
                self.results[subagent_id] = SubagentResult(
                    id=subagent_id,
                    status=SubagentStatus.FAILED,
                    error=str(e),
                )

        future = self.executor.submit(run)
        self.active_subagents[subagent_id] = future

        return subagent_id

    def run_sync(
        self,
        task: str,
        tools: dict[str, Callable] | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 50,
        timeout: float = 300.0,
    ) -> SubagentResult:
        """Run a subagent task synchronously.

        Args:
            task: Task description
            tools: Tool handlers
            system_prompt: Override system prompt
            max_iterations: Max iterations
            timeout: Timeout in seconds

        Returns:
            Subagent result
        """
        import time

        subagent_id = self.run_async(task, tools, system_prompt, max_iterations)
        start = time.time()

        while subagent_id in self.active_subagents:
            if time.time() - start > timeout:
                self.cancel(subagent_id)
                return SubagentResult(
                    id=subagent_id,
                    status=SubagentStatus.FAILED,
                    error=f"Timeout after {timeout}s",
                )
            time.sleep(0.1)

        return self.results.get(
            subagent_id,
            SubagentResult(id=subagent_id, status=SubagentStatus.FAILED, error="Not found"),
        )

    def get_result(self, subagent_id: str) -> SubagentResult | None:
        """Get a subagent result.

        Args:
            subagent_id: Subagent ID

        Returns:
            Result or None
        """
        # Check if completed
        if subagent_id in self.active_subagents:
            future = self.active_subagents[subagent_id]
            if future.done():
                del self.active_subagents[subagent_id]
                return self.results.get(subagent_id)
            return None

        return self.results.get(subagent_id)

    def cancel(self, subagent_id: str) -> bool:
        """Cancel a subagent.

        Args:
            subagent_id: Subagent ID

        Returns:
            True if cancelled
        """
        if subagent_id in self.active_subagents:
            self.active_subagents[subagent_id].cancel()
            del self.active_subagents[subagent_id]
            self.results[subagent_id] = SubagentResult(
                id=subagent_id,
                status=SubagentStatus.CANCELLED,
                error="Cancelled by user",
            )
            return True
        return False

    def list_active(self) -> list[str]:
        """List active subagent IDs.

        Returns:
            List of IDs
        """
        return list(self.active_subagents.keys())

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor.

        Args:
            wait: Wait for pending tasks
        """
        self.executor.shutdown(wait=wait)
