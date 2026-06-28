"""Permission guard for small-claude-code.

The permission guard provides:
- Allow/deny rules for tools
- Path-based access control
- Approval workflow for sensitive operations
"""

import fnmatch
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable


class PermissionAction(str, Enum):
    """Permission action result."""

    ALLOW = "allow"
    DENY = "deny"
    APPROVE = "approve"


@dataclass
class PermissionResult:
    """Result of a permission check."""

    action: PermissionAction
    reason: str


class PermissionRule:
    """Base class for permission rules."""

    def check(self, tool_name: str, params: dict) -> PermissionResult | None:
        """Check if this rule applies.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            PermissionResult if rule applies, None otherwise
        """
        raise NotImplementedError


class AllowRule(PermissionRule):
    """Allow tool execution."""

    def __init__(self, tool_name: str = "*", pattern: str = "*"):
        """Initialize allow rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Glob pattern for matching
        """
        self.tool_name = tool_name
        self.pattern = pattern

    def check(self, tool_name: str, params: dict) -> PermissionResult | None:
        if self.tool_name != "*" and self.tool_name != tool_name:
            return None

        if tool_name == "bash":
            command = params.get("command", "")
            if not fnmatch.fnmatch(command, self.pattern):
                return None
        elif tool_name == "read" or tool_name == "write" or tool_name == "edit":
            path = params.get("path", "")
            if not fnmatch.fnmatch(path, self.pattern):
                return None

        return PermissionResult(
            action=PermissionAction.ALLOW,
            reason=f"Allowed by {self.__class__.__name__}: {self.tool_name}",
        )


class DenyRule(PermissionRule):
    """Deny tool execution."""

    def __init__(self, tool_name: str = "*", pattern: str = "*", reason: str = "Denied"):
        """Initialize deny rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Glob pattern for matching
            reason: Denial reason
        """
        self.tool_name = tool_name
        self.pattern = pattern
        self.reason = reason

    def check(self, tool_name: str, params: dict) -> PermissionResult | None:
        if self.tool_name != "*" and self.tool_name != tool_name:
            return None

        if tool_name == "bash":
            command = params.get("command", "")
            if not fnmatch.fnmatch(command, self.pattern):
                return None
        elif tool_name in ("read", "write", "edit"):
            path = params.get("path", "")
            if not fnmatch.fnmatch(path, self.pattern):
                return None

        return PermissionResult(
            action=PermissionAction.DENY,
            reason=self.reason,
        )


class ApproveRule(PermissionRule):
    """Require approval for tool execution."""

    def __init__(self, tool_name: str = "*", pattern: str = "*"):
        """Initialize approval rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Glob pattern for matching
        """
        self.tool_name = tool_name
        self.pattern = pattern

    def check(self, tool_name: str, params: dict) -> PermissionResult | None:
        if self.tool_name != "*" and self.tool_name != tool_name:
            return None

        if tool_name == "bash":
            command = params.get("command", "")
            if not fnmatch.fnmatch(command, self.pattern):
                return None
        elif tool_name in ("read", "write", "edit"):
            path = params.get("path", "")
            if not fnmatch.fnmatch(path, self.pattern):
                return None

        return PermissionResult(
            action=PermissionAction.APPROVE,
            reason="Requires approval",
        )


class PermissionGuard:
    """Permission guard for tool execution."""

    def __init__(self):
        """Initialize the permission guard."""
        self.rules: list[PermissionRule] = []
        self.approval_callback: Callable | None = None

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a permission rule.

        Args:
            rule: Permission rule to add
        """
        self.rules.append(rule)

    def allow(self, tool_name: str = "*", pattern: str = "*") -> "PermissionGuard":
        """Add an allow rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Pattern to match

        Returns:
            Self for chaining
        """
        self.add_rule(AllowRule(tool_name, pattern))
        return self

    def deny(self, tool_name: str = "*", pattern: str = "*", reason: str = "Denied") -> "PermissionGuard":
        """Add a deny rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Pattern to match
            reason: Denial reason

        Returns:
            Self for chaining
        """
        self.add_rule(DenyRule(tool_name, pattern, reason))
        return self

    def approve(self, tool_name: str = "*", pattern: str = "*") -> "PermissionGuard":
        """Add an approval rule.

        Args:
            tool_name: Tool name or * for all
            pattern: Pattern to match

        Returns:
            Self for chaining
        """
        self.add_rule(ApproveRule(tool_name, pattern))
        return self

    def set_approval_callback(self, callback: Callable) -> None:
        """Set the approval callback.

        Args:
            callback: Function to call for approvals
        """
        self.approval_callback = callback

    def check(self, tool_name: str, params: dict) -> PermissionResult:
        """Check if a tool can be executed.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            PermissionResult
        """
        for rule in self.rules:
            result = rule.check(tool_name, params)
            if result:
                if result.action == PermissionAction.APPROVE and self.approval_callback:
                    approved = self.approval_callback(tool_name, params)
                    if approved:
                        return PermissionResult(
                            action=PermissionAction.ALLOW,
                            reason="Approved by callback",
                        )
                return result

        # Default: deny
        return PermissionResult(
            action=PermissionAction.DENY,
            reason="No matching rule found",
        )

    def wrap_tool(self, tool_func: Callable) -> Callable:
        """Wrap a tool function with permission checks.

        Args:
            tool_func: Tool function to wrap

        Returns:
            Wrapped function
        """

        def wrapper(**kwargs):
            result = self.check(tool_func.__name__, kwargs)
            if result.action == PermissionAction.DENY:
                return f"Permission denied: {result.reason}"
            elif result.action == PermissionAction.APPROVE:
                return "Awaiting approval..."
            return tool_func(**kwargs)

        return wrapper
