from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FILES = [
    "AI_KB_MASTER_INDEX.md",
    "llm-agent-engineering-deep-dive.md",
    "agent-evaluation-benchmark.md",
    "prompt-and-tool-guardrails.md",
    "ai-domain-index-and-checklist.md",
    "ai-model-selection-and-routing-strategy.md",
    "ai-rag-engineering-playbook.md",
    "ai-agent-memory-context-management.md",
    "ai-data-security-and-compliance-playbook.md",
    "ai-red-team-and-safety-evaluation.md",
    "ai-release-readiness-and-rollback-gate.md",
    "ai-observability-and-oncall-runbook.md",
    "ai-cost-capacity-optimization-playbook.md",
    "ai-governance-maturity-model.md",
    "ai-stage-exit-criteria.yaml",
    "ai-catalog.yaml",
]

REQUIRED_MD_SECTIONS = ["### 目标", "### 适用范围", "### 执行清单", "### 验收标准", "### 常见失败模式", "### 回滚策略"]
REQUIRED_AI_STAGES = [
    "requirement",
    "design",
    "architecture",
    "implementation",
    "evaluation",
    "release",
    "operations",
    "incident_learning",
]
QUALITY_CHECK_FILES = [
    "llm-agent-engineering-deep-dive.md",
    "agent-evaluation-benchmark.md",
    "prompt-and-tool-guardrails.md",
    "ai-domain-index-and-checklist.md",
    "ai-model-selection-and-routing-strategy.md",
    "ai-rag-engineering-playbook.md",
    "ai-agent-memory-context-management.md",
    "ai-data-security-and-compliance-playbook.md",
    "ai-red-team-and-safety-evaluation.md",
    "ai-release-readiness-and-rollback-gate.md",
    "ai-observability-and-oncall-runbook.md",
    "ai-cost-capacity-optimization-playbook.md",
    "ai-governance-maturity-model.md",
]


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _check_md_sections(ai_root: Path) -> list[str]:
    missing: list[str] = []
    for name in QUALITY_CHECK_FILES:
        text = _load_text(ai_root / name)
        if not text:
            continue
        not_found = [section for section in REQUIRED_MD_SECTIONS if section not in text]
        if not_found:
            missing.append(f"{name}: {','.join(not_found)}")
    return missing


def _check_ai_stages(ai_root: Path) -> list[str]:
    text = _load_text(ai_root / "ai-stage-exit-criteria.yaml")
    missing = []
    for stage in REQUIRED_AI_STAGES:
        if f"  {stage}:" not in text:
            missing.append(stage)
    return missing



def build_report(root: Path) -> dict:
    ai_root = root / "knowledge" / "ai"
    missing_md_sections = _check_md_sections(ai_root)
    missing_ai_stages = _check_ai_stages(ai_root)
    missing_files = [name for name in REQUIRED_FILES if not (ai_root / name).exists()]
    total_files = sum(1 for p in ai_root.rglob("*") if p.is_file()) if ai_root.exists() else 0
    return {
        "ai_root": str(ai_root),
        "total_files": total_files,
        "required_files": REQUIRED_FILES,
        "missing_files": missing_files,
        "missing_md_sections": missing_md_sections,
        "missing_ai_stages": missing_ai_stages,
        "is_ai_knowledge_base_grade": total_files >= 15
        and len(missing_files) == 0
        and len(missing_md_sections) == 0
        and len(missing_ai_stages) == 0,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
