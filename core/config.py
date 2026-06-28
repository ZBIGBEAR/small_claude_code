"""Configuration management for small-claude-code."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration for the agent harness."""

    # Model settings
    model: str = "claude-sonnet-4-20250514"
    api_key: Optional[str] = None
    api_base: str = "https://api.anthropic.com/v1"

    # System prompt
    system_prompt: str = "You are a helpful AI assistant."

    # Working directory
    workdir: Path = field(default_factory=lambda: Path.cwd())

    # Permission settings
    allow_bash: bool = True
    allow_write: bool = True
    allow_read: bool = True
    allowed_paths: list[str] = field(default_factory=list)

    # Hook settings
    hooks_enabled: bool = True

    # Context settings
    max_tokens: int = 200000
    context_budget: int = 150000

    # Task settings
    tasks_dir: Path = field(
        default_factory=lambda: Path.home() / ".claude" / "tasks"
    )

    # Memory settings
    memory_enabled: bool = True
    memory_dir: Path = field(
        default_factory=lambda: Path.home() / ".claude" / "memory"
    )

    # Skill settings
    skills_dir: Path = field(
        default_factory=lambda: Path.home() / ".claude" / "skills"
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        config = cls()

        if api_key := os.environ.get("ANTHROPIC_API_KEY"):
            config.api_key = api_key
        if api_base := os.environ.get("ANTHROPIC_API_BASE"):
            config.api_base = api_base
        if model := os.environ.get("CLAUDE_MODEL"):
            config.model = model
        if workdir := os.environ.get("CLAUDE_WORKDIR"):
            config.workdir = Path(workdir)
        if tasks_dir := os.environ.get("CLAUDE_TASKS_DIR"):
            config.tasks_dir = Path(tasks_dir)
        if memory_dir := os.environ.get("CLAUDE_MEMORY_DIR"):
            config.memory_dir = Path(memory_dir)
        if skills_dir := os.environ.get("CLAUDE_SKILLS_DIR"):
            config.skills_dir = Path(skills_dir)

        return config

    def ensure_dirs(self) -> None:
        """Ensure required directories exist."""
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
