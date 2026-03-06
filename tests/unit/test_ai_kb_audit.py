from pathlib import Path
import importlib.util


def _load_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "audit_ai_kb.py"
    spec = importlib.util.spec_from_file_location("audit_ai_kb", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_ai_kb_audit_fails_when_missing(temp_project_dir: Path):
    build_report = _load_module().build_report
    report = build_report(temp_project_dir)
    assert report["is_ai_knowledge_base_grade"] is False
    assert len(report["missing_files"]) > 0


def test_ai_kb_audit_passes_with_required_files(temp_project_dir: Path):
    module = _load_module()
    ai_root = temp_project_dir / "knowledge" / "ai"
    md_content = "\n".join(
        [
            "# 开发：Excellent（11964948@qq.com）",
            "",
            "### 目标",
            "- x",
            "### 适用范围",
            "- x",
            "### 执行清单",
            "- x",
            "### 验收标准",
            "- x",
            "### 常见失败模式",
            "- x",
            "### 回滚策略",
            "- x",
            "",
        ]
    )
    for name in module.REQUIRED_FILES:
        if name.endswith(".yaml"):
            _write(
                ai_root / name,
                "\n".join(
                    [
                        "ai_stage_exit_criteria:",
                        "  requirement:",
                        "  design:",
                        "  architecture:",
                        "  implementation:",
                        "  evaluation:",
                        "  release:",
                        "  operations:",
                        "  incident_learning:",
                    ]
                ),
            )
        else:
            _write(ai_root / name, md_content)
    report = module.build_report(temp_project_dir)
    assert report["is_ai_knowledge_base_grade"] is True
    assert report["missing_files"] == []
    assert report["missing_md_sections"] == []
    assert report["missing_ai_stages"] == []
