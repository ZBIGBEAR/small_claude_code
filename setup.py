#!/usr/bin/env python3
"""Setup script for small-claude-code.

This setup.py handles the unusual case where the package directory name
(small-claude-code with hyphens) differs from the import name
(small_claude_code with underscores).
"""

from setuptools import setup

setup(
    name="small-claude-code",
    version="1.0.0",
    description="A lightweight agent harness framework inspired by Claude Code",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="small-claude-code",
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ],
    },
    # Map import name to directory
    packages=["small_claude_code", "small_claude_code.core",
              "small_claude_code.tools", "small_claude_code.permission",
              "small_claude_code.hooks", "small_claude_code.task",
              "small_claude_code.context", "small_claude_code.memory",
              "small_claude_code.skill", "small_claude_code.subagent"],
    package_dir={"small_claude_code": "."},
    include_package_data=True,
    zip_safe=False,
)
