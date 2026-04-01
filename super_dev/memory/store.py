"""
持久化记忆存储 — 4 种记忆类型 + MEMORY.md 索引

记忆文件格式:
    ---
    name: Memory title
    description: One-line relevance description
    type: user|feedback|project|reference
    created_at: ISO-8601
    updated_at: ISO-8601
    ---
    Content here ...

所有记忆文件存放在 memory_dir 目录中，以 MEMORY.md 作为索引。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_logger = logging.getLogger("super_dev.memory.store")

MEMORY_TYPES = ("user", "feedback", "project", "reference")
MAX_INDEX_LINES = 200
MAX_INDEX_BYTES = 25 * 1024  # 25 KB

# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------


@dataclass
class MemoryEntry:
    """一条记忆记录。"""

    name: str
    description: str
    type: str  # user | feedback | project | reference
    filename: str
    content: str
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if self.type not in MEMORY_TYPES:
            _logger.warning("Unknown memory type '%s'; expected one of %s", self.type, MEMORY_TYPES)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_frontmatter_md(self) -> str:
        """Render as Markdown with YAML frontmatter."""
        lines = [
            "---",
            f"name: {self.name}",
            f"description: {self.description}",
            f"type: {self.type}",
            f"created_at: {self.created_at}",
            f"updated_at: {self.updated_at}",
            "---",
            "",
            self.content,
        ]
        return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n(.*)",
    re.DOTALL,
)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (metadata_dict, body) from a frontmatter markdown file."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta_block, body = m.group(1), m.group(2)
    meta: dict[str, str] = {}
    for line in meta_block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, body.strip()


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


class MemoryStore:
    """持久化记忆存储。"""

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, entry: MemoryEntry) -> Path:
        """Save a memory entry to disk. Returns the file path."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        path = self.memory_dir / entry.filename
        path.write_text(entry.to_frontmatter_md(), encoding="utf-8")

        _logger.info("Saved memory '%s' -> %s", entry.name, path)
        self.update_index()
        return path

    def load(self, filename: str) -> MemoryEntry | None:
        """Load a single memory entry by filename."""
        path = self.memory_dir / filename
        if not path.exists():
            return None
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            _logger.warning("Failed to read memory file %s: %s", path, exc)
            return None

        meta, body = _parse_frontmatter(text)
        if not meta.get("name"):
            return None

        return MemoryEntry(
            name=meta.get("name", ""),
            description=meta.get("description", ""),
            type=meta.get("type", "project"),
            filename=filename,
            content=body,
            created_at=meta.get("created_at", ""),
            updated_at=meta.get("updated_at", ""),
        )

    def list_all(self) -> list[MemoryEntry]:
        """List all memory entries in the directory."""
        if not self.memory_dir.exists():
            return []
        entries: list[MemoryEntry] = []
        for path in sorted(self.memory_dir.glob("*.md")):
            if path.name == "MEMORY.md":
                continue
            entry = self.load(path.name)
            if entry is not None:
                entries.append(entry)
        return entries

    def find_duplicate(self, name: str, type: str) -> MemoryEntry | None:
        """Find an existing entry with the same name and type."""
        for entry in self.list_all():
            if entry.name == name and entry.type == type:
                return entry
        return None

    def delete(self, filename: str) -> bool:
        """Delete a memory file. Returns True if deleted."""
        path = self.memory_dir / filename
        if not path.exists():
            return False
        path.unlink()
        _logger.info("Deleted memory file %s", path)
        self.update_index()
        return True

    def scan(self) -> list[dict[str, Any]]:
        """Scan directory for memory files with frontmatter metadata."""
        if not self.memory_dir.exists():
            return []
        results: list[dict[str, Any]] = []
        for path in sorted(self.memory_dir.glob("*.md")):
            if path.name == "MEMORY.md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            meta, _body = _parse_frontmatter(text)
            if meta:
                meta["filename"] = path.name
                results.append(meta)
        return results

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def update_index(self) -> None:
        """Regenerate MEMORY.md index from all memory files."""
        entries = self.list_all()
        lines: list[str] = ["# Memory Index", ""]

        # Group by type
        by_type: dict[str, list[MemoryEntry]] = {}
        for entry in entries:
            by_type.setdefault(entry.type, []).append(entry)

        for mtype in MEMORY_TYPES:
            group = by_type.get(mtype, [])
            if not group:
                continue
            lines.append(f"## {mtype.capitalize()}")
            lines.append("")
            for entry in group:
                date_part = entry.updated_at[:10] if entry.updated_at else ""
                desc = entry.description or entry.name
                lines.append(f"- [{entry.name}]({entry.filename}) — {date_part} {desc}")
            lines.append("")

        text = "\n".join(lines) + "\n"

        # Enforce size limits
        if len(text.encode("utf-8")) > MAX_INDEX_BYTES:
            truncated_lines = text.splitlines()[:MAX_INDEX_LINES]
            truncated_lines.append("")
            truncated_lines.append("_(index truncated — too many entries)_")
            text = "\n".join(truncated_lines) + "\n"

        index_path = self.memory_dir / "MEMORY.md"
        index_path.write_text(text, encoding="utf-8")
        _logger.debug("Updated memory index at %s (%d entries)", index_path, len(entries))
