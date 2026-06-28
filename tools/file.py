"""File operation tools for small-claude-code."""

from pathlib import Path

from .base import BaseTool, ToolResult


class ReadTool(BaseTool):
    """Read a file."""

    name = "read"
    description = "Read the contents of a file."

    def __init__(self, workdir: str | None = None):
        """Initialize the read tool.

        Args:
            workdir: Working directory
        """
        super().__init__(workdir)

    def execute(self, path: str, offset: int = 0, limit: int | None = None) -> ToolResult:
        """Read a file.

        Args:
            path: File path
            offset: Line offset
            limit: Maximum lines to read

        Returns:
            File contents
        """
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = Path(self.workdir) / file_path

            if not file_path.exists():
                return ToolResult(
                    success=False,
                    content="",
                    error=f"File not found: {path}",
                )

            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            if offset > 0:
                lines = lines[offset:]
            if limit:
                lines = lines[:limit]

            return ToolResult(success=True, content="\n".join(lines))

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))


class WriteTool(BaseTool):
    """Write a file."""

    name = "write"
    description = "Write content to a file."

    def __init__(self, workdir: str | None = None):
        """Initialize the write tool.

        Args:
            workdir: Working directory
        """
        super().__init__(workdir)

    def execute(self, path: str, content: str, append: bool = False) -> ToolResult:
        """Write to a file.

        Args:
            path: File path
            content: Content to write
            append: Append mode

        Returns:
            Success message
        """
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = Path(self.workdir) / file_path

            file_path.parent.mkdir(parents=True, exist_ok=True)

            if append:
                file_path.write_text(content, encoding="utf-8", append=True)
            else:
                file_path.write_text(content, encoding="utf-8")

            return ToolResult(
                success=True,
                content=f"Written to {file_path}",
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))


class EditTool(BaseTool):
    """Edit a file using string replacement."""

    name = "edit"
    description = "Edit a file using old_string/new_string replacement."

    def __init__(self, workdir: str | None = None):
        """Initialize the edit tool.

        Args:
            workdir: Working directory
        """
        super().__init__(workdir)

    def execute(
        self, path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> ToolResult:
        """Edit a file.

        Args:
            path: File path
            old_string: String to replace
            new_string: Replacement string
            replace_all: Replace all occurrences

        Returns:
            Success message
        """
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = Path(self.workdir) / file_path

            if not file_path.exists():
                return ToolResult(
                    success=False,
                    content="",
                    error=f"File not found: {path}",
                )

            content = file_path.read_text(encoding="utf-8")

            if replace_all:
                new_content = content.replace(old_string, new_string)
                count = new_content.count(new_string)
            else:
                if old_string not in content:
                    return ToolResult(
                        success=False,
                        content="",
                        error=f"String not found: {old_string[:100]}...",
                    )
                new_content = content.replace(old_string, new_string, 1)
                count = 1

            file_path.write_text(new_content, encoding="utf-8")

            return ToolResult(
                success=True,
                content=f"Edited {count} occurrence(s) in {file_path}",
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))
