"""Hook system for small-claude-code.

Hooks provide extension points around tool execution:
- pre_tool: Called before a tool is executed
- post_tool: Called after a tool is executed
- pre_run: Called before the agent loop starts
- post_run: Called after the agent loop ends
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class HookType(str, Enum):
    """Hook type enumeration."""

    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    PRE_RUN = "pre_run"
    POST_RUN = "post_run"


@dataclass
class Hook:
    """A hook function."""

    name: str
    hook_type: HookType
    func: Callable
    description: str = ""

    def __repr__(self) -> str:
        return f"Hook({self.name}, {self.hook_type.value})"


class HookManager:
    """Manager for hooks in the harness."""

    def __init__(self):
        """Initialize the hook manager."""
        self.hooks: list[Hook] = []

    def register(
        self,
        name: str,
        hook_type: HookType,
        func: Callable,
        description: str = "",
    ) -> None:
        """Register a hook.

        Args:
            name: Hook name
            hook_type: Type of hook
            func: Hook function
            description: Hook description
        """
        # Remove existing hook with same name
        self.hooks = [h for h in self.hooks if h.name != name]
        self.hooks.append(Hook(name, hook_type, func, description))

    def unregister(self, name: str) -> None:
        """Unregister a hook.

        Args:
            name: Hook name
        """
        self.hooks = [h for h in self.hooks if h.name != name]

    def pre_tool(self, name: str, func: Callable, description: str = "") -> None:
        """Register a pre-tool hook.

        Args:
            name: Hook name
            func: Function to call
            description: Hook description
        """
        self.register(name, HookType.PRE_TOOL, func, description)

    def post_tool(self, name: str, func: Callable, description: str = "") -> None:
        """Register a post-tool hook.

        Args:
            name: Hook name
            func: Function to call
            description: Hook description
        """
        self.register(name, HookType.POST_TOOL, func, description)

    def pre_run(self, name: str, func: Callable, description: str = "") -> None:
        """Register a pre-run hook.

        Args:
            name: Hook name
            func: Function to call
            description: Hook description
        """
        self.register(name, HookType.PRE_RUN, func, description)

    def post_run(self, name: str, func: Callable, description: str = "") -> None:
        """Register a post-run hook.

        Args:
            name: Hook name
            func: Function to call
            description: Hook description
        """
        self.register(name, HookType.POST_RUN, func, description)

    def trigger(self, hook_type: HookType, **kwargs) -> None:
        """Trigger all hooks of a given type.

        Args:
            hook_type: Type of hook to trigger
            **kwargs: Arguments to pass to hook functions
        """
        for hook in self.hooks:
            if hook.hook_type == hook_type:
                try:
                    hook.func(**kwargs)
                except Exception as e:
                    print(f"Hook {hook.name} failed: {e}")

    def list_hooks(self) -> list[Hook]:
        """List all registered hooks.

        Returns:
            List of hooks
        """
        return self.hooks


# Built-in hook implementations


def log_pre_tool(tool_name: str, params: dict) -> None:
    """Log pre-tool execution.

    Args:
        tool_name: Tool name
        params: Tool parameters
    """
    print(f"[HOOK] Pre-tool: {tool_name}({params})")


def log_post_tool(tool_name: str, result: Any) -> None:
    """Log post-tool execution.

    Args:
        tool_name: Tool name
        result: Tool result
    """
    content = result.content if hasattr(result, "content") else str(result)
    print(f"[HOOK] Post-tool: {tool_name} -> {content[:100]}")
