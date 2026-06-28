"""Tests for small-claude-code core modules."""

import pytest
from small_claude_code.core.config import Config
from small_claude_code.core.message import Message, MessageRole, ContentBlock


class TestConfig:
    """Tests for Config class."""

    def test_config_default_values(self):
        """Test default configuration values."""
        config = Config()
        assert config.model == "claude-sonnet-4-20250514"
        assert config.api_key is None
        assert config.max_tokens == 200000

    def test_config_from_env(self):
        """Test creating config from environment."""
        import os

        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        os.environ["CLAUDE_MODEL"] = "test-model"

        config = Config.from_env()
        assert config.api_key == "test-key"
        assert config.model == "test-model"

        # Cleanup
        del os.environ["ANTHROPIC_API_KEY"]
        del os.environ["CLAUDE_MODEL"]

    def test_config_ensure_dirs(self, tmp_path):
        """Test directory creation."""
        config = Config(
            workdir=tmp_path / "workdir",
            tasks_dir=tmp_path / "tasks",
            memory_dir=tmp_path / "memory",
        )
        config.ensure_dirs()

        assert (tmp_path / "workdir").exists()
        assert (tmp_path / "tasks").exists()
        assert (tmp_path / "memory").exists()


class TestMessage:
    """Tests for Message class."""

    def test_user_message(self):
        """Test creating a user message."""
        msg = Message.user("Hello")
        assert msg.role == MessageRole.USER
        assert len(msg.content) == 1
        assert msg.content[0].type == "text"
        assert msg.content[0].text == "Hello"

    def test_assistant_message_with_text(self):
        """Test creating an assistant message with text."""
        blocks = [ContentBlock.text_block("Hello, world!")]
        msg = Message.assistant(blocks)
        assert msg.role == MessageRole.ASSISTANT
        assert len(msg.content) == 1
        assert msg.content[0].type == "text"

    def test_message_to_dict(self):
        """Test converting message to API format."""
        msg = Message.user("Hello")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert len(d["content"]) == 1


class TestContentBlock:
    """Tests for ContentBlock class."""

    def test_text_block(self):
        """Test creating a text block."""
        block = ContentBlock.text_block("Hello")
        assert block.type == "text"
        assert block.text == "Hello"

    def test_tool_use_block(self):
        """Test creating a tool use block."""
        block = ContentBlock.tool_use_block(
            id="tool-1",
            name="bash",
            input={"command": "ls"},
        )
        assert block.type == "tool_use"
        assert block.tool_use.id == "tool-1"
        assert block.tool_use.name == "bash"
        assert block.tool_use.input == {"command": "ls"}

    def test_tool_result_block(self):
        """Test creating a tool result block."""
        block = ContentBlock.tool_result_block(
            tool_use_id="tool-1",
            content="output",
        )
        assert block.type == "tool_result"
        assert block.tool_result_id == "tool-1"
        assert block.tool_result_content == "output"
