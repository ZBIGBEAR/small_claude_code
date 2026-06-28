"""Message handling for Claude Harness."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_RESULT = "tool_result"


@dataclass
class ToolUse:
    """Tool use block from the model."""

    id: str
    name: str
    input: dict[str, Any]


@dataclass
class ContentBlock:
    """Content block in a message."""

    type: str
    text: Optional[str] = None
    tool_use: Optional[ToolUse] = None
    tool_result_id: Optional[str] = None
    tool_result_content: Optional[str] = None

    @classmethod
    def text_block(cls, text: str) -> "ContentBlock":
        """Create a text content block."""
        return cls(type="text", text=text)

    @classmethod
    def tool_use_block(
        cls, id: str, name: str, input: dict[str, Any]
    ) -> "ContentBlock":
        """Create a tool use content block."""
        return cls(
            type="tool_use",
            tool_use=ToolUse(id=id, name=name, input=input),
        )

    @classmethod
    def tool_result_block(
        cls, tool_use_id: str, content: str
    ) -> "ContentBlock":
        """Create a tool result content block."""
        return cls(
            type="tool_result",
            tool_result_id=tool_use_id,
            tool_result_content=content,
        )


@dataclass
class Message:
    """A message in the conversation."""

    role: MessageRole
    content: list[ContentBlock] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert message to API format."""
        content = []
        for block in self.content:
            if block.type == "text":
                content.append({"type": "text", "text": block.text or ""})
            elif block.type == "tool_use":
                content.append(
                    {
                        "type": "tool_use",
                        "id": block.tool_use.id,
                        "name": block.tool_use.name,
                        "input": block.tool_use.input,
                    }
                )
            elif block.type == "tool_result":
                content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.tool_result_id,
                        "content": block.tool_result_content or "",
                    }
                )
        return {"role": self.role.value, "content": content}

    @classmethod
    def user(cls, text: str) -> "Message":
        """Create a user message."""
        return cls(role=MessageRole.USER, content=[ContentBlock.text_block(text)])

    @classmethod
    def user_with_results(cls, results: list[dict]) -> "Message":
        """Create a user message from tool results."""
        content = []
        for result in results:
            content.append(
                ContentBlock.tool_result_block(
                    tool_use_id=result["tool_use_id"],
                    content=result["content"],
                )
            )
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: list[ContentBlock]) -> "Message":
        """Create an assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content)
