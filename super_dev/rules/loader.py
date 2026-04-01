"""Load and match conditional rules from ``.super-dev/rules/*.md``.

Rule files use YAML frontmatter to declare which paths they apply to:

.. code-block:: markdown

    ---
    paths: ["app/**/*.tsx", "components/**"]
    ---
    # React Component Rules
    - All components must use TypeScript
    - Props must be typed with interface, not type

Negative patterns (prefixed with ``!``) exclude matching paths.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ConditionalRule:
    """A rule loaded from ``.super-dev/rules/*.md``."""

    name: str
    content: str
    paths: list[str] = field(default_factory=list)
    source: str = ""


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def load_rules(project_dir: Path) -> list[ConditionalRule]:
    """Load all conditional rules from ``.super-dev/rules/*.md``."""
    rules_dir = project_dir / ".super-dev" / "rules"
    if not rules_dir.is_dir():
        return []

    rules: list[ConditionalRule] = []
    for md_file in sorted(rules_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        paths: list[str] = []
        content = text

        match = _FRONTMATTER_RE.match(text)
        if match:
            try:
                meta = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                meta = {}
            raw_paths = meta.get("paths", [])
            if isinstance(raw_paths, list):
                paths = [str(p) for p in raw_paths]
            content = text[match.end() :]

        rules.append(
            ConditionalRule(
                name=md_file.stem,
                content=content.strip(),
                paths=paths,
                source=str(md_file),
            )
        )

    return rules


def match_rules(
    rules: list[ConditionalRule],
    target_path: str,
) -> list[ConditionalRule]:
    """Return rules whose path patterns match *target_path*.

    Rules with an empty ``paths`` list match everything.  Negative patterns
    (starting with ``!``) exclude the target even if a positive pattern matched.
    """
    matched: list[ConditionalRule] = []
    for rule in rules:
        if not rule.paths:
            # No path constraint -- always applies.
            matched.append(rule)
            continue

        included = False
        excluded = False
        for pattern in rule.paths:
            if pattern.startswith("!"):
                if fnmatch.fnmatch(target_path, pattern[1:]):
                    excluded = True
            else:
                if fnmatch.fnmatch(target_path, pattern):
                    included = True

        if included and not excluded:
            matched.append(rule)

    return matched
