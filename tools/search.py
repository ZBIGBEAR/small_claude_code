"""Search tools for small-claude-code."""

import re
from pathlib import Path

from .base import BaseTool, ToolResult


class GlobTool(BaseTool):
    """Find files matching a pattern."""

    name = "glob"
    description = "Find files matching a glob pattern."

    def __init__(self, workdir: str | None = None):
        """Initialize the glob tool.

        Args:
            workdir: Working directory
        """
        super().__init__(workdir)

    def execute(self, pattern: str, path: str | None = None) -> ToolResult:
        """Find files matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            path: Directory to search (default: workdir)

        Returns:
            List of matching files
        """
        try:
            search_path = Path(path or self.workdir)
            if not search_path.is_absolute():
                search_path = Path(self.workdir) / search_path

            matches = list(search_path.glob(pattern))

            if not matches:
                return ToolResult(
                    success=True,
                    content="No matches found",
                )

            result = "\n".join(str(m.relative_to(search_path.parent)) for m in matches)
            return ToolResult(
                success=True,
                content=f"Found {len(matches)} file(s):\n{result}",
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))


class GrepTool(BaseTool):
    """Search for pattern in files."""

    name = "grep"
    description = "Search for a pattern in files."

    def __init__(self, workdir: str | None = None):
        """Initialize the grep tool.

        Args:
            workdir: Working directory
        """
        super().__init__(workdir)

    def execute(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        context: int = 0,
    ) -> ToolResult:
        """Search for a pattern.

        Args:
            pattern: Regex pattern to search
            path: File or directory to search
            glob: Only match files matching glob
            context: Lines of context to show

        Returns:
            Matching lines with context
        """
        try:
            search_path = Path(path or self.workdir)
            if not search_path.is_absolute():
                search_path = Path(self.workdir) / search_path

            regex = re.compile(pattern)
            matches = []

            files_to_search = []
            if search_path.is_file():
                files_to_search = [search_path]
            elif search_path.is_dir():
                if glob:
                    files_to_search = list(search_path.glob(f"**/{glob}"))
                else:
                    files_to_search = list(search_path.glob("**/*"))

            for file_path in files_to_search:
                if not file_path.is_file():
                    continue

                try:
                    lines = file_path.read_text(encoding="utf-8", errors="ignore").split(
                        "\n"
                    )
                    for i, line in enumerate(lines, 1):
                        if regex.search(line):
                            if context > 0:
                                start = max(0, i - context - 1)
                                end = min(len(lines), i + context)
                                for j in range(start, end):
                                    prefix = ">>> " if j == i - 1 else "    "
                                    matches.append(f"{file_path}:{j + 1}{prefix}{lines[j]}")
                            else:
                                matches.append(f"{file_path}:{i}:{line}")
                except Exception:
                    continue

            if not matches:
                return ToolResult(success=True, content="No matches found")

            result = "\n".join(matches[:100])  # Limit output
            if len(matches) > 100:
                result += f"\n... and {len(matches) - 100} more matches"

            return ToolResult(
                success=True,
                content=f"Found {len(matches)} match(es):\n{result}",
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))
