"""Skill loader for small-claude-code.

Skills are modular extensions that provide:
- Specialized tool sets
- Domain-specific knowledge
- Reusable prompt templates
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class Skill:
    """A skill module."""

    name: str
    description: str
    version: str = "1.0.0"
    tools: dict[str, Callable] = field(default_factory=dict)
    system_prompt: str = ""
    commands: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_manifest(self) -> dict:
        """Convert to skill manifest.

        Returns:
            Skill manifest dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tools": list(self.tools.keys()),
            "commands": self.commands,
            "metadata": self.metadata,
        }


class SkillLoader:
    """Loader for skill modules."""

    def __init__(self, skills_dir: str | Path | None = None):
        """Initialize the skill loader.

        Args:
            skills_dir: Directory containing skills
        """
        self.skills_dir = Path(skills_dir or Path.home() / ".claude" / "skills")
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_skills: dict[str, Skill] = {}
        self.active_skill: str | None = None

    def load_skill(self, skill_path: str | Path) -> Skill | None:
        """Load a skill from a path.

        Args:
            skill_path: Path to skill directory or manifest

        Returns:
            Loaded skill or None
        """
        skill_path = Path(skill_path)

        if skill_path.is_dir():
            manifest_file = skill_path / "SKILL.md"
        else:
            manifest_file = skill_path

        if not manifest_file.exists():
            return None

        try:
            # Parse SKILL.md
            content = manifest_file.read_text(encoding="utf-8")

            # Simple frontmatter parsing
            metadata = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            metadata[key.strip()] = value.strip()
                    content = parts[2]

            # Extract name from first heading
            name = metadata.get("name", skill_path.name)

            skill = Skill(
                name=name,
                description=metadata.get("description", ""),
                version=metadata.get("version", "1.0.0"),
                metadata=metadata,
            )

            self.loaded_skills[skill.name] = skill
            return skill

        except Exception as e:
            print(f"Failed to load skill from {skill_path}: {e}")
            return None

    def load_all(self) -> list[Skill]:
        """Load all skills from the skills directory.

        Returns:
            List of loaded skills
        """
        skills = []

        for item in self.skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill = self.load_skill(item)
                if skill:
                    skills.append(skill)

        return skills

    def get_skill(self, name: str) -> Skill | None:
        """Get a loaded skill by name.

        Args:
            name: Skill name

        Returns:
            Skill or None
        """
        return self.loaded_skills.get(name)

    def activate_skill(self, name: str) -> bool:
        """Activate a skill.

        Args:
            name: Skill name

        Returns:
            True if activated
        """
        if name in self.loaded_skills:
            self.active_skill = name
            return True
        return False

    def deactivate_skill(self) -> None:
        """Deactivate the current skill."""
        self.active_skill = None

    def get_active_skill(self) -> Skill | None:
        """Get the currently active skill.

        Returns:
            Active skill or None
        """
        if self.active_skill:
            return self.loaded_skills.get(self.active_skill)
        return None

    def get_all_skills(self) -> list[Skill]:
        """Get all loaded skills.

        Returns:
            List of skills
        """
        return list(self.loaded_skills.values())

    def create_skill_manifest(
        self,
        name: str,
        description: str,
        tools: list[str] | None = None,
        commands: list[str] | None = None,
    ) -> str:
        """Create a skill manifest template.

        Args:
            name: Skill name
            description: Skill description
            tools: List of tool names
            commands: List of commands

        Returns:
            Manifest content
        """
        manifest = f"""---
name: {name}
description: {description}
version: 1.0.0
---

# {name}

{description}

## Usage

Describe how to use this skill.

## Tools

{", ".join(tools) if tools else "No additional tools."}

## Commands

{", ".join(commands) if commands else "No commands."}
"""
        return manifest
