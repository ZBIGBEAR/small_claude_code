"""Tests for small-claude-code tools."""

import pytest
from pathlib import Path
from small_claude_code.tools.base import BaseTool, ToolResult
from small_claude_code.tools.bash import BashTool
from small_claude_code.tools.file import ReadTool, WriteTool, EditTool
from small_claude_code.tools.search import GlobTool, GrepTool


class TestToolResult:
    """Tests for ToolResult class."""

    def test_success_result(self):
        """Test successful result."""
        result = ToolResult(success=True, content="output")
        d = result.to_dict()
        assert d["success"] is True
        assert d["content"] == "output"

    def test_error_result(self):
        """Test error result."""
        result = ToolResult(success=False, content="", error="Something went wrong")
        d = result.to_dict()
        assert d["success"] is False
        assert d["error"] == "Something went wrong"


class TestBashTool:
    """Tests for BashTool."""

    def test_echo_command(self, tmp_path):
        """Test echo command."""
        tool = BashTool(workdir=str(tmp_path))
        result = tool.execute("echo 'Hello, World!'")
        assert result.success is True
        assert "Hello, World!" in result.content

    def test_failed_command(self):
        """Test failed command."""
        tool = BashTool()
        result = tool.execute("exit 1")
        # exit 1 is not an error for the tool, just returns non-zero
        assert result.success is True

    def test_nonexistent_command(self):
        """Test nonexistent command."""
        tool = BashTool()
        result = tool.execute("nonexistent_command_xyz")
        assert result.success is False
        assert "command not found" in result.error.lower()


class TestReadTool:
    """Tests for ReadTool."""

    def test_read_file(self, tmp_path):
        """Test reading a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        tool = ReadTool(workdir=str(tmp_path))
        result = tool.execute("test.txt")

        assert result.success is True
        assert "Hello, World!" in result.content

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a nonexistent file."""
        tool = ReadTool(workdir=str(tmp_path))
        result = tool.execute("nonexistent.txt")

        assert result.success is False
        assert "not found" in result.error.lower()


class TestWriteTool:
    """Tests for WriteTool."""

    def test_write_file(self, tmp_path):
        """Test writing a file."""
        tool = WriteTool(workdir=str(tmp_path))
        result = tool.execute("test.txt", "Hello, World!")

        assert result.success is True
        assert (tmp_path / "test.txt").read_text() == "Hello, World!"

    def test_write_absolute_path(self, tmp_path):
        """Test writing with absolute path."""
        tool = WriteTool(workdir=str(tmp_path))
        target = tmp_path / "subdir" / "test.txt"
        result = tool.execute(str(target), "Hello!")

        assert result.success is True
        assert target.read_text() == "Hello!"


class TestEditTool:
    """Tests for EditTool."""

    def test_edit_file(self, tmp_path):
        """Test editing a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        tool = EditTool(workdir=str(tmp_path))
        result = tool.execute(
            path="test.txt",
            old_string="World",
            new_string="Python",
        )

        assert result.success is True
        assert test_file.read_text() == "Hello, Python!"

    def test_edit_nonexistent_file(self, tmp_path):
        """Test editing a nonexistent file."""
        tool = EditTool(workdir=str(tmp_path))
        result = tool.execute(
            path="nonexistent.txt",
            old_string="a",
            new_string="b",
        )

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_edit_string_not_found(self, tmp_path):
        """Test editing with string not found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello!")

        tool = EditTool(workdir=str(tmp_path))
        result = tool.execute(
            path="test.txt",
            old_string="nonexistent",
            new_string="found",
        )

        assert result.success is False
        assert "not found" in result.error.lower()


class TestGlobTool:
    """Tests for GlobTool."""

    def test_glob_files(self, tmp_path):
        """Test globbing for files."""
        (tmp_path / "test1.txt").write_text("1")
        (tmp_path / "test2.txt").write_text("2")
        (tmp_path / "other.log").write_text("3")

        tool = GlobTool(workdir=str(tmp_path))
        result = tool.execute("*.txt")

        assert result.success is True
        assert "test1.txt" in result.content
        assert "test2.txt" in result.content
        assert "other.log" not in result.content


class TestGrepTool:
    """Tests for GrepTool."""

    def test_grep_file(self, tmp_path):
        """Test grepping for a pattern."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line 1: hello\nline 2: world\nline 3: hello again")

        tool = GrepTool(workdir=str(tmp_path))
        result = tool.execute("hello", path="test.txt")

        assert result.success is True
        assert "test.txt" in result.content
        assert "hello" in result.content
