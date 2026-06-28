"""Base tool class for small-claude-code."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolResult:
    """Result from a tool execution."""

    success: bool
    content: str
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        if self.success:
            return {"success": True, "content": self.content}
        return {"success": False, "error": self.error or "Unknown error"}


class BaseTool:
    """Base class for tools."""

    name: str = ""
    description: str = ""

    def __init__(self, workdir: str | None = None):
        """Initialize the tool.

        Args:
            workdir: Working directory for the tool
        """
        self.workdir = workdir or "."

    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            Tool result
        """
        raise NotImplementedError

    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format.

        Returns:
            Tool specification in function calling format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {}},
            },
        }


def create_tool_handler(tool: BaseTool) -> Callable:
    """Create a handler function from a tool.

    Args:
        tool: Tool instance

    Returns:
        Handler function
    """

    def handler(**kwargs) -> str:
        result = tool.execute(**kwargs)
        if result.success:
            return result.content
        return f"Error: {result.error}"

    handler.__name__ = tool.name
    handler.__doc__ = tool.description
    return handler
