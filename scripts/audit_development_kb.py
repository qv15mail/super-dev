from __future__ import annotations

import json
from pathlib import Path


REQUIRED_SECTIONS = [
    "00-governance",
    "01-standards",
    "02-playbooks",
    "03-checklists",
    "04-antipatterns",
    "05-cases",
    "06-glossary",
    "07-learning-path",
    "08-catalog",
    "09-maturity",
    "10-knowledge-graph",
    "11-ui-excellence",
    "12-scenarios",
    "13-implementation-assets",
    "14-full-lifecycle",
    "15-lifecycle-templates",
]


def build_report(root: Path) -> dict:
    dev_root = root / "knowledge" / "development"
    section_counts = {}
    for section in REQUIRED_SECTIONS:
        path = dev_root / section
        section_counts[section] = sum(1 for p in path.rglob("*") if p.is_file()) if path.exists() else 0
    total_files = sum(1 for p in dev_root.rglob("*") if p.is_file()) if dev_root.exists() else 0
    missing_sections = [s for s, c in section_counts.items() if c == 0]
    return {
        "development_root": str(dev_root),
        "total_files": total_files,
        "section_counts": section_counts,
        "missing_sections": missing_sections,
        "is_knowledge_base_grade": total_files >= 110 and len(missing_sections) == 0,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
