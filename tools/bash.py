"""Bash tool for small-claude-code."""

import subprocess
from pathlib import Path

from .base import BaseTool, ToolResult


class BashTool(BaseTool):
    """Execute bash commands."""

    name = "bash"
    description = "Execute a bash command and return the output."

    def __init__(self, workdir: str | None = None, timeout: int = 30):
        """Initialize the bash tool.

        Args:
            workdir: Working directory
            timeout: Command timeout in seconds
        """
        super().__init__(workdir)
        self.timeout = timeout

    def execute(self, command: str, cwd: str | None = None) -> ToolResult:
        """Execute a bash command.

        Args:
            command: Command to execute
            cwd: Working directory (optional)

        Returns:
            Command output
        """
        try:
            cwd = cwd or self.workdir
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr

            # Check for command not found errors
            if "command not found" in result.stderr or result.returncode == 127:
                return ToolResult(
                    success=False,
                    content=output,
                    error=f"Command not found: {command[:50]}",
                )

            if result.returncode != 0:
                return ToolResult(
                    success=True,
                    content=output,
                )

            return ToolResult(success=True, content=output)

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                content="",
                error=f"Command timed out after {self.timeout}s",
            )
        except Exception as e:
            return ToolResult(success=False, content="", error=str(e))


class PythonTool(BaseTool):
    """Execute Python code."""

    name = "python"
    description = "Execute Python code and return the output."

    def __init__(self, workdir: str | None = None, timeout: int = 30):
        """Initialize the Python tool.

        Args:
            workdir: Working directory
            timeout: Execution timeout in seconds
        """
        super().__init__(workdir)
        self.timeout = timeout

    def execute(self, code: str) -> ToolResult:
        """Execute Python code.

        Args:
            code: Python code to execute

        Returns:
            Execution output
        """
        import io
        import sys

        try:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            exec(code, {"__name__": "__main__"})

            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            output = stdout
            if stderr:
                output += "\nSTDERR:\n" + stderr

            return ToolResult(success=True, content=output)

        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return ToolResult(success=False, content="", error=str(e))
