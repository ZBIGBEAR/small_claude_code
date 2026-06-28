"""Memory store for small-claude-code.

The memory system provides:
- Entity extraction and storage
- Conversation memory
- Cross-session persistence
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MemoryEntry:
    """A memory entry."""

    id: str
    type: str  # "entity", "fact", "preference", "conversation"
    content: str
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }


class MemoryStore:
    """Persistent memory store."""

    def __init__(self, memory_dir: str | Path | None = None):
        """Initialize the memory store.

        Args:
            memory_dir: Directory for memory storage
        """
        self.memory_dir = Path(memory_dir or Path.home() / ".claude" / "memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.entries_file = self.memory_dir / "entries.json"
        self.entries: dict[str, MemoryEntry] = {}
        self._load()

    def _load(self) -> None:
        """Load memory from disk."""
        if self.entries_file.exists():
            try:
                data = json.loads(self.entries_file.read_text())
                self.entries = {
                    k: MemoryEntry(**v) for k, v in data.items()
                }
            except Exception:
                pass

    def _save(self) -> None:
        """Save memory to disk."""
        data = {k: v.to_dict() for k, v in self.entries.items()}
        self.entries_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def add(
        self,
        content: str,
        entry_type: str = "fact",
        metadata: dict | None = None,
    ) -> MemoryEntry:
        """Add a memory entry.

        Args:
            content: Memory content
            entry_type: Type of memory
            metadata: Additional metadata

        Returns:
            Created entry
        """
        entry_id = f"mem-{int(time.time() * 1000)}-{len(self.entries)}"
        entry = MemoryEntry(
            id=entry_id,
            type=entry_type,
            content=content,
            metadata=metadata or {},
        )

        self.entries[entry_id] = entry
        self._save()

        return entry

    def get(self, entry_id: str) -> MemoryEntry | None:
        """Get a memory entry.

        Args:
            entry_id: Entry ID

        Returns:
            Entry or None
        """
        if entry_id in self.entries:
            entry = self.entries[entry_id]
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
            self._save()
            return entry
        return None

    def search(
        self,
        query: str,
        entry_type: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search memory entries.

        Args:
            query: Search query
            entry_type: Filter by type
            limit: Maximum results

        Returns:
            Matching entries
        """
        results = []
        query_lower = query.lower()

        for entry in self.entries.values():
            if entry_type and entry.type != entry_type:
                continue
            if query_lower in entry.content.lower():
                results.append(entry)

        # Sort by relevance (access_count and recency)
        results.sort(
            key=lambda e: (e.access_count, e.last_accessed),
            reverse=True,
        )

        return results[:limit]

    def update(self, entry_id: str, content: str | None = None) -> MemoryEntry | None:
        """Update a memory entry.

        Args:
            entry_id: Entry ID
            content: New content

        Returns:
            Updated entry or None
        """
        if entry_id not in self.entries:
            return None

        entry = self.entries[entry_id]
        if content:
            entry.content = content
        entry.updated_at = datetime.now().isoformat()

        self._save()
        return entry

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry.

        Args:
            entry_id: Entry ID

        Returns:
            True if deleted
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save()
            return True
        return False

    def get_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context for a query.

        Args:
            query: Query string
            limit: Maximum context entries

        Returns:
            Formatted context string
        """
        entries = self.search(query, limit=limit)
        if not entries:
            return ""

        context_parts = []
        for entry in entries:
            context_parts.append(f"[{entry.type}] {entry.content}")

        return "\n".join(context_parts)

    def clear(self) -> None:
        """Clear all memory."""
        self.entries.clear()
        self._save()
