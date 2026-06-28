"""Core agent loop for small-claude-code.

The agent loop is the heart of the harness. It:
1. Sends messages to the model
2. Handles tool use requests
3. Manages the conversation state
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import anthropic

from .config import Config
from .message import ContentBlock, Message, MessageRole


@dataclass
class ToolResult:
    """Result from a tool execution."""

    tool_use_id: str
    tool_name: str
    content: str
    error: bool = False


@dataclass
class LoopStats:
    """Statistics for the agent loop."""

    iterations: int = 0
    tool_calls: int = 0
    total_time: float = 0.0


class AgentLoop:
    """Core agent loop that coordinates the model and tools."""

    def __init__(self, config: Config):
        """Initialize the agent loop.

        Args:
            config: Configuration for the harness
        """
        self.config = config
        self.client = anthropic.Anthropic(
            api_key=config.api_key,
            base_url=config.api_base,
        )
        self.tools: dict[str, Callable] = {}
        self.hooks: list[Callable] = []
        self.messages: list[Message] = []

    def register_tool(self, name: str, handler: Callable) -> None:
        """Register a tool handler.

        Args:
            name: Tool name
            handler: Function to call for this tool
        """
        self.tools[name] = handler

    def register_hook(self, hook: Callable) -> None:
        """Register a hook function.

        Args:
            hook: Function to call before/after tool execution
        """
        self.hooks.append(hook)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.

        Args:
            message: Message to add
        """
        self.messages.append(message)

    def clear_messages(self) -> None:
        """Clear all messages."""
        self.messages = []

    def run(
        self,
        user_message: str,
        max_iterations: int = 100,
    ) -> str:
        """Run the agent loop.

        Args:
            user_message: Initial user message
            max_iterations: Maximum number of iterations

        Returns:
            Final text response from the model
        """
        self.messages.append(Message.user(user_message))
        stats = LoopStats()
        start_time = time.time()

        for i in range(max_iterations):
            stats.iterations += 1

            # Build API messages
            api_messages = [msg.to_dict() for msg in self.messages]

            # Call the model
            response = self._call_model(api_messages)

            # Check stop reason
            if response.stop_reason != "tool_use":
                # Add assistant's final response
                text_content = []
                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        text_content.append(block.text)
                final_text = "\n".join(text_content)
                self.messages.append(Message.assistant(response.content))
                stats.total_time = time.time() - start_time
                return final_text

            # Handle tool uses
            tool_results = self._handle_tool_calls(response.content)
            stats.tool_calls += len(tool_results)

            # Add tool results as user message
            results_dict = [
                {
                    "tool_use_id": r.tool_use_id,
                    "content": r.content,
                }
                for r in tool_results
            ]
            self.messages.append(Message.user_with_results(results_dict))

        stats.total_time = time.time() - start_time
        raise RuntimeError(f"Max iterations ({max_iterations}) exceeded")

    def _call_model(self, messages: list[dict]) -> Any:
        """Call the model API.

        Args:
            messages: Messages in API format

        Returns:
            Model response
        """
        system_prompt = (
            self.config.system_prompt
            if self.config.system_prompt
            else "You are a helpful AI assistant."
        )

        # Build tools list
        tools = []
        for name, handler in self.tools.items():
            # Get tool description from handler
            desc = handler.__doc__ or f"Tool: {name}"
            tools.append(
                {
                    "name": name,
                    "description": desc.strip().split("\n")[0],
                    "input_schema": {"type": "object", "properties": {}},
                }
            )

        response = self.client.messages.create(
            model=self.config.model,
            system=system_prompt,
            messages=messages,
            max_tokens=4096,
            tools=tools if tools else None,
        )

        return response

    def _handle_tool_calls(self, content_blocks: list) -> list[ToolResult]:
        """Handle tool use calls from the model.

        Args:
            content_blocks: Content blocks from the model response

        Returns:
            List of tool results
        """
        results = []

        for block in content_blocks:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            tool_id = block.id

            # Execute pre-hooks
            for hook in self.hooks:
                if hook.__name__.startswith("pre_"):
                    hook(tool_name, tool_input)

            # Execute tool
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**tool_input)
                    results.append(
                        ToolResult(
                            tool_use_id=tool_id,
                            tool_name=tool_name,
                            content=str(result),
                        )
                    )
                except Exception as e:
                    results.append(
                        ToolResult(
                            tool_use_id=tool_id,
                            tool_name=tool_name,
                            content=f"Error: {str(e)}",
                            error=True,
                        )
                    )
            else:
                results.append(
                    ToolResult(
                        tool_use_id=tool_id,
                        tool_name=tool_name,
                        content=f"Unknown tool: {tool_name}",
                        error=True,
                    )
                )

            # Execute post-hooks
            for hook in self.hooks:
                if hook.__name__.startswith("post_"):
                    hook(tool_name, results[-1])

        return results

    def get_stats(self) -> LoopStats:
        """Get current loop statistics."""
        return self._stats
