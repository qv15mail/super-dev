import json
from pathlib import Path
from zipfile import ZipFile

from super_dev.deployers.delivery import DeliveryPackager


def _write(path: Path, content: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_required_files(temp_project_dir: Path, name: str) -> None:
    output_dir = temp_project_dir / "output"
    _write(output_dir / f"{name}-research.md")
    _write(output_dir / f"{name}-prd.md")
    _write(output_dir / f"{name}-architecture.md")
    _write(output_dir / f"{name}-uiux.md")
    _write(output_dir / f"{name}-execution-plan.md")
    _write(output_dir / f"{name}-frontend-blueprint.md")
    _write(output_dir / f"{name}-redteam.md")
    _write(output_dir / f"{name}-quality-gate.md")
    _write(output_dir / f"{name}-code-review.md")
    _write(output_dir / f"{name}-ai-prompt.md")
    _write(output_dir / f"{name}-task-execution.md")
    _write(output_dir / f"{name}-frontend-runtime.md")
    _write(output_dir / f"{name}-frontend-runtime.json", '{"passed": true}')

    _write(output_dir / "frontend" / "index.html")
    _write(output_dir / "frontend" / "styles.css")
    _write(output_dir / "frontend" / "app.js")
    _write(temp_project_dir / "preview.html")

    _write(temp_project_dir / "backend" / "API_CONTRACT.md")
    _write(temp_project_dir / ".env.deploy.example")
    _write(output_dir / "deploy" / "all-secrets-checklist.md")

    _write(temp_project_dir / ".github" / "workflows" / "ci.yml")
    _write(temp_project_dir / ".github" / "workflows" / "cd.yml")
    _write(temp_project_dir / ".gitlab-ci.yml")
    _write(temp_project_dir / "Jenkinsfile")
    _write(temp_project_dir / ".azure-pipelines.yml")
    _write(temp_project_dir / "bitbucket-pipelines.yml")

    _write(temp_project_dir / "prisma" / "migrations" / "0001_init" / "migration.sql")
    _write(
        temp_project_dir / ".super-dev" / "changes" / "demo" / "tasks.md",
        "# Tasks\n\n- [x] **1.1: done**\n",
    )


def test_delivery_packager_ready(temp_project_dir: Path) -> None:
    name = "demo"
    _seed_required_files(temp_project_dir, name)

    packager = DeliveryPackager(project_dir=temp_project_dir, name=name, version="2.0.4")
    result = packager.package(cicd_platform="all")

    assert result["status"] == "ready"
    assert result["missing_required_count"] == 0

    manifest_path = Path(str(result["manifest_file"]))
    report_path = Path(str(result["report_file"]))
    archive_path = Path(str(result["archive_file"]))

    assert manifest_path.exists()
    assert report_path.exists()
    assert archive_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "ready"
    assert "output/demo-prd.md" in manifest["included_files"]
    assert "prisma/migrations/0001_init/migration.sql" in manifest["included_files"]
    assert manifest["spec_tasks"]["pending"] == 0

    with ZipFile(archive_path, "r") as archive:
        entries = set(archive.namelist())
        assert "output/demo-prd.md" in entries
        assert "output/delivery/demo-delivery-manifest.json" in entries


def test_delivery_packager_incomplete_without_migrations(temp_project_dir: Path) -> None:
    name = "demo"
    _seed_required_files(temp_project_dir, name)
    migration_dir = temp_project_dir / "prisma" / "migrations"
    for file_path in migration_dir.rglob("*"):
        if file_path.is_file():
            file_path.unlink()

    packager = DeliveryPackager(project_dir=temp_project_dir, name=name, version="2.0.4")
    result = packager.package(cicd_platform="all")

    assert result["status"] == "incomplete"
    assert result["missing_required_count"] >= 1

    missing_items = result["missing_required"]
    assert isinstance(missing_items, list)
    missing_paths = {item["path"] for item in missing_items if isinstance(item, dict)}
    assert "migrations/*" in missing_paths


def test_delivery_packager_incomplete_with_pending_spec_tasks(temp_project_dir: Path) -> None:
    name = "demo"
    _seed_required_files(temp_project_dir, name)
    (temp_project_dir / ".super-dev" / "changes" / "demo" / "tasks.md").write_text(
        "# Tasks\n\n- [ ] **1.1: pending**\n",
        encoding="utf-8",
    )

    packager = DeliveryPackager(project_dir=temp_project_dir, name=name, version="2.0.4")
    result = packager.package(cicd_platform="all")

    assert result["status"] == "incomplete"
    missing_items = result["missing_required"]
    assert isinstance(missing_items, list)
    reasons = {item["path"] for item in missing_items if isinstance(item, dict)}
    assert ".super-dev/changes/*/tasks.md" in reasons


def test_delivery_packager_incomplete_without_frontend_runtime_report(temp_project_dir: Path) -> None:
    name = "demo"
    _seed_required_files(temp_project_dir, name)
    (temp_project_dir / "output" / f"{name}-frontend-runtime.md").unlink()
    (temp_project_dir / "output" / f"{name}-frontend-runtime.json").unlink()

    packager = DeliveryPackager(project_dir=temp_project_dir, name=name, version="2.0.4")
    result = packager.package(cicd_platform="all")

    assert result["status"] == "incomplete"
    missing_items = result["missing_required"]
    assert isinstance(missing_items, list)
    reasons = {item["path"] for item in missing_items if isinstance(item, dict)}
    assert f"output/{name}-frontend-runtime.md" in reasons
    assert f"output/{name}-frontend-runtime.json" in reasons
