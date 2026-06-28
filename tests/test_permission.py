"""Tests for small-claude-code permission module."""

import pytest
from small_claude_code.permission.guard import (
    PermissionGuard,
    PermissionRule,
    AllowRule,
    DenyRule,
    ApproveRule,
    PermissionAction,
)


class TestAllowRule:
    """Tests for AllowRule."""

    def test_allow_all_tools(self):
        """Test allowing all tools."""
        rule = AllowRule()
        result = rule.check("bash", {"command": "ls"})
        assert result is not None
        assert result.action == PermissionAction.ALLOW

    def test_allow_specific_tool(self):
        """Test allowing specific tool."""
        rule = AllowRule(tool_name="bash")
        result = rule.check("bash", {"command": "ls"})
        assert result.action == PermissionAction.ALLOW

        result = rule.check("read", {"path": "file.txt"})
        assert result is None


class TestDenyRule:
    """Tests for DenyRule."""

    def test_deny_all_tools(self):
        """Test denying all tools."""
        rule = DenyRule()
        result = rule.check("bash", {"command": "ls"})
        assert result is not None
        assert result.action == PermissionAction.DENY

    def test_deny_specific_pattern(self):
        """Test denying specific pattern."""
        rule = DenyRule(tool_name="bash", pattern="rm -rf *")
        result = rule.check("bash", {"command": "rm -rf /"})
        assert result is not None
        assert result.action == PermissionAction.DENY
        assert "Denied" in result.reason

        result = rule.check("bash", {"command": "ls"})
        assert result is None


class TestApproveRule:
    """Tests for ApproveRule."""

    def test_approve_tool(self):
        """Test approval rule."""
        rule = ApproveRule(tool_name="bash")
        result = rule.check("bash", {"command": "ls"})
        assert result is not None
        assert result.action == PermissionAction.APPROVE


class TestPermissionGuard:
    """Tests for PermissionGuard."""

    def test_default_deny(self):
        """Test default deny when no rules match."""
        guard = PermissionGuard()
        result = guard.check("bash", {"command": "ls"})
        assert result.action == PermissionAction.DENY

    def test_allow_specific(self):
        """Test allowing specific tool."""
        guard = PermissionGuard()
        guard.allow("read", "*.txt")

        result = guard.check("read", {"path": "file.txt"})
        assert result.action == PermissionAction.ALLOW

        result = guard.check("read", {"path": "file.py"})
        assert result.action == PermissionAction.DENY

    def test_deny_specific(self):
        """Test denying specific tool."""
        guard = PermissionGuard()
        guard.deny("bash", "rm -rf *")  # Deny rm -rf first
        guard.allow("*", "*")  # Then allow everything else

        result = guard.check("bash", {"command": "rm -rf /"})
        assert result.action == PermissionAction.DENY

        result = guard.check("bash", {"command": "ls"})
        assert result.action == PermissionAction.ALLOW

    def test_approval_workflow(self):
        """Test approval workflow - APPROVE requires callback to convert to ALLOW."""
        guard = PermissionGuard()
        guard.approve("bash")  # No callback set

        result = guard.check("bash", {"command": "ls"})
        assert result.action == PermissionAction.APPROVE

    def test_approval_with_callback(self):
        """Test approval with callback approval."""
        guard = PermissionGuard()

        def callback(tool_name, params):
            return True  # Auto-approve

        guard.set_approval_callback(callback)
        guard.approve("bash")

        result = guard.check("bash", {"command": "ls"})
        assert result.action == PermissionAction.ALLOW
