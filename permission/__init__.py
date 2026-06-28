"""Permission module for small-claude-code."""

from .guard import (
    PermissionGuard,
    PermissionRule,
    PermissionAction,
    PermissionResult,
    AllowRule,
    DenyRule,
    ApproveRule,
)

__all__ = [
    "PermissionGuard",
    "PermissionRule",
    "PermissionAction",
    "PermissionResult",
    "AllowRule",
    "DenyRule",
    "ApproveRule",
]
