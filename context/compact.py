"""Context compaction for small-claude-code.

Context compaction strategies to handle long conversations:
- snip: Remove middle messages
- microCompact: Summarize and replace messages
- toolResultBudget: Limit tool result storage
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class CompactionResult:
    """Result of context compaction."""

    original_count: int
    compacted_count: int
    removed_count: int
    method: str


class ContextCompactor:
    """Context compactor for long conversations."""

    def __init__(
        self,
        max_messages: int = 100,
        max_tool_results: int = 20,
        budget_tokens: int = 150000,
    ):
        """Initialize the context compactor.

        Args:
            max_messages: Maximum number of messages to keep
            max_tool_results: Maximum tool results to keep
            budget_tokens: Token budget for compaction
        """
        self.max_messages = max_messages
        self.max_tool_results = max_tool_results
        self.budget_tokens = budget_tokens
        self.snip_func: Callable | None = None
        self.micro_compact_func: Callable | None = None

    def set_snip_func(self, func: Callable) -> None:
        """Set the snip function for message removal.

        Args:
            func: Function that takes messages and returns compacted list
        """
        self.snip_func = func

    def set_micro_compact_func(self, func: Callable) -> None:
        """Set the micro-compact function for summarization.

        Args:
            func: Function that takes messages and returns summarized version
        """
        self.micro_compact_func = func

    def compact(self, messages: list) -> CompactionResult:
        """Compact the message history.

        Args:
            messages: List of messages

        Returns:
            Compaction result
        """
        original_count = len(messages)
        method = "none"

        # Strategy 1: Remove tool results beyond limit
        messages = self._compact_tool_results(messages)
        if len(messages) < original_count:
            method = "tool_result_budget"

        # Strategy 2: Snip middle messages if still over limit
        if len(messages) > self.max_messages and self.snip_func:
            messages = self.snip_func(messages)
            method = "snip"

        # Strategy 3: Micro-compact if still over budget
        if len(messages) > self.max_messages and self.micro_compact_func:
            messages = self.micro_compact_func(messages)
            method = "micro_compact"

        return CompactionResult(
            original_count=original_count,
            compacted_count=len(messages),
            removed_count=original_count - len(messages),
            method=method,
        )

    def _compact_tool_results(self, messages: list) -> list:
        """Compact tool results.

        Args:
            messages: List of messages

        Returns:
            Compacted messages
        """
        tool_results_kept = 0
        compacted = []

        for msg in messages:
            if msg.get("role") == "user" and isinstance(msg.get("content"), list):
                new_content = []
                for block in msg["content"]:
                    if block.get("type") == "tool_result":
                        if tool_results_kept < self.max_tool_results:
                            new_content.append(block)
                            tool_results_kept += 1
                        # Skip excess tool results
                    else:
                        new_content.append(block)
                compacted.append({**msg, "content": new_content})
            else:
                compacted.append(msg)

        return compacted


def default_snip(messages: list, keep_first: int = 5, keep_last: int = 20) -> list:
    """Default snip function - keeps first N and last N messages.

    Args:
        messages: List of messages
        keep_first: Number of first messages to keep
        keep_last: Number of last messages to keep

    Returns:
        Snipped messages
    """
    if len(messages) <= keep_first + keep_last:
        return messages

    return messages[:keep_first] + [
        {
            "role": "system",
            "content": f"[{len(messages) - keep_first - keep_last} messages removed by context compaction]",
        }
    ] + messages[-keep_last:]
