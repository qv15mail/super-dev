from pathlib import Path

from super_dev.analyzer import ProductAuditBuilder


def test_product_audit_detects_missing_product_audit_doc(temp_project_dir: Path) -> None:
    docs_dir = temp_project_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "QUICKSTART.md").write_text("super-dev start --idea\n当前阶段是 `research`\n", encoding="utf-8")
    (docs_dir / "HOST_USAGE_GUIDE.md").write_text("super-dev start --idea\n当前阶段是 `research`\n", encoding="utf-8")
    (docs_dir / "WORKFLOW_GUIDE.md").write_text("super-dev review docs\nsuper-dev run --resume\nsuper-dev review quality\n", encoding="utf-8")

    builder = ProductAuditBuilder(temp_project_dir)
    report = builder.build()

    assert any(item.title.startswith("缺少关键产品文档") for item in report.findings)


def test_product_audit_writes_report(temp_project_dir: Path) -> None:
    docs_dir = temp_project_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "QUICKSTART.md").write_text("super-dev start --idea\n当前阶段是 `research`\n", encoding="utf-8")
    (docs_dir / "HOST_USAGE_GUIDE.md").write_text("super-dev start --idea\n当前阶段是 `research`\n", encoding="utf-8")
    (docs_dir / "WORKFLOW_GUIDE.md").write_text("super-dev review docs\nsuper-dev run --resume\nsuper-dev review quality\n", encoding="utf-8")
    (docs_dir / "PRODUCT_AUDIT.md").write_text("super-dev product-audit\nproof-pack\nrelease readiness\n", encoding="utf-8")

    builder = ProductAuditBuilder(temp_project_dir)
    report = builder.build()
    files = builder.write(report)

    assert files["markdown"].exists()
    assert files["json"].exists()
