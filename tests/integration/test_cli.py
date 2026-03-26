"""
Super Dev CLI 集成测试
"""

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import super_dev.cli as cli_module
from super_dev import __version__ as _super_dev_version
from super_dev.cli import SuperDevCLI
from super_dev.integrations import IntegrationManager
from super_dev.review_state import save_docs_confirmation, save_ui_revision
from super_dev.skills import SkillManager
from super_dev.specs.generator import SpecGenerator


def _confirm_docs(temp_project_dir: Path) -> None:
    save_docs_confirmation(
        temp_project_dir,
        {
            "status": "confirmed",
            "comment": "测试中预先确认三文档",
            "actor": "pytest",
            "run_id": "test-run",
        },
    )


def _prepare_release_ready_project(project_dir: Path) -> None:
    (project_dir / "super_dev").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / ".super-dev" / "changes" / "release-hardening-finalization").mkdir(
        parents=True,
        exist_ok=True,
    )
    (project_dir / "pyproject.toml").write_text(f'[project]\nversion = "{_super_dev_version}"\n[project.scripts]\nsuper-dev = "super_dev.cli:main"\n', encoding="utf-8")
    (project_dir / ".gitignore").write_text(
        "\n".join(
            [
                "output/",
                "artifacts/",
                ".super-dev/runs/",
                ".super-dev/review-state/",
                "/.agent/",
                "/.claude/",
                "/.codebuddy/",
                "/.cursor/",
                "/.gemini/",
                "/.iflow/",
                "/.kimi/",
                "/.kiro/",
                "/.opencode/",
                "/.qoder/",
                "/.trae/",
                "/.openclaw/",
                "/.windsurf/",
                "/GEMINI.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / "super_dev" / "__init__.py").write_text(f'__version__ = "{_super_dev_version}"\n', encoding="utf-8")
    (project_dir / "README.md").write_text(
        f"当前版本：`{_super_dev_version}`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "README_EN.md").write_text(
        f"Current version: `{_super_dev_version}`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_USAGE_GUIDE.md").write_text("Smoke\n/super-dev\nsuper-dev:\n", encoding="utf-8")
    (project_dir / "docs" / "HOST_CAPABILITY_AUDIT.md").write_text("官方依据\nsuper-dev integrate smoke\n", encoding="utf-8")
    (project_dir / "docs" / "README.md").write_text("用户文档\n维护者文档\n", encoding="utf-8")
    (project_dir / "docs" / "WORKFLOW_GUIDE.md").write_text("super-dev review docs\nsuper-dev run --resume\n", encoding="utf-8")
    (project_dir / "docs" / "WORKFLOW_GUIDE_EN.md").write_text("super-dev review docs\nsuper-dev run --resume\n", encoding="utf-8")
    (project_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    for name in ("change.yaml", "proposal.md", "tasks.md"):
        (project_dir / ".super-dev" / "changes" / "release-hardening-finalization" / name).write_text("ok\n", encoding="utf-8")


def _prepare_proof_pack_project(project_dir: Path) -> None:
    _prepare_release_ready_project(project_dir)
    output_dir = project_dir / "output"
    (output_dir / "delivery").mkdir(parents=True, exist_ok=True)
    (output_dir / "rehearsal").mkdir(parents=True, exist_ok=True)
    for suffix in ("research", "prd", "architecture", "uiux"):
        (output_dir / f"{project_dir.name}-{suffix}.md").write_text("# ok\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-frontend-runtime.json").write_text('{"passed": true}', encoding="utf-8")
    (output_dir / f"{project_dir.name}-ui-review.json").write_text(
        json.dumps({"score": 92, "critical_count": 0}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{project_dir.name}-quality-gate.md").write_text("# quality gate\npassed\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-repo-map.md").write_text("# Repo Map\n\nok\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-repo-map.json").write_text(
        json.dumps({"project_name": project_dir.name}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{project_dir.name}-dependency-graph.md").write_text("# Dependency Graph\n\nok\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-dependency-graph.json").write_text(
        json.dumps({"project_name": project_dir.name, "node_count": 4, "edge_count": 3}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{project_dir.name}-impact-analysis.md").write_text("# Change Impact Analysis\n\nok\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-impact-analysis.json").write_text(
        json.dumps({"project_name": project_dir.name, "risk_level": "medium"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{project_dir.name}-regression-guard.md").write_text("# Regression Guard\n\nok\n", encoding="utf-8")
    (output_dir / f"{project_dir.name}-regression-guard.json").write_text(
        json.dumps({"project_name": project_dir.name, "risk_level": "medium"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / f"{project_dir.name}-prd.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## 2. 功能范围",
                "",
                "### 用户登录",
                "- 支持邮箱密码登录",
                "",
                "### 运营看板",
                "- 提供运营数据概览",
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / "delivery" / f"{project_dir.name}-delivery-manifest.json").write_text(
        json.dumps({"status": "ready"}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "rehearsal" / f"{project_dir.name}-rehearsal-report.json").write_text(
        json.dumps({"passed": True, "score": 95}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    save_docs_confirmation(
        project_dir,
        {
            "status": "confirmed",
            "comment": "proof pack docs confirmed",
            "actor": "pytest",
            "run_id": "proof-pack-run",
        },
    )
    save_ui_revision(
        project_dir,
        {
            "status": "confirmed",
            "comment": "ui revision closed",
            "actor": "pytest",
            "run_id": "proof-pack-run",
        },
    )
    generator = SpecGenerator(project_dir)
    generator.init_sdd()
    change = generator.create_change(
        change_id="proof-quality",
        title="Proof Quality",
        description="proof pack spec quality",
    )
    generator.scaffold_change_artifacts(change.id)
    (project_dir / ".super-dev" / "changes" / change.id / "tasks.md").write_text(
        "# Tasks\n\n- [x] 支持邮箱密码登录\n- [x] 提供运营数据概览\n",
        encoding="utf-8",
    )


class TestCLIInit:
    """测试 init 命令"""

    def test_init_creates_config(self, temp_project_dir: Path):
        """测试 init 命令创建配置文件"""
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            cli = SuperDevCLI()
            result = cli.run([
                "init", "test-project",
                "-p", "web",
                "-f", "next",
                "-b", "node"
            ])

            assert result == 0
            config_path = temp_project_dir / "super-dev.yaml"
            assert config_path.exists()
            assert (temp_project_dir / ".super-dev" / "WORKFLOW.md").exists()
            assert (temp_project_dir / "output" / "test-project-bootstrap.md").exists()

            with open(config_path) as f:
                config = yaml.safe_load(f)
                assert config["name"] == "test-project"
                assert config["platform"] == "web"
        finally:
            os.chdir(original_cwd)

    def test_init_already_initialized(self, temp_project_dir: Path):
        """测试重复初始化"""
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            # 创建现有配置
            (Path.cwd() / "super-dev.yaml").write_text("name: existing")

            cli = SuperDevCLI()
            result = cli.run(["init", "another-project"])

            assert result == 0  # 应该优雅处理
        finally:
            os.chdir(original_cwd)

    def test_bootstrap_creates_visible_contract_artifacts(self, temp_project_dir: Path):
        """测试显式 bootstrap 命令"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            cli = SuperDevCLI()
            result = cli.run([
                "bootstrap",
                "--name", "bootstrap-demo",
                "--platform", "web",
                "--frontend", "next",
                "--backend", "node",
            ])

            assert result == 0
            assert (temp_project_dir / "super-dev.yaml").exists()
            workflow_file = temp_project_dir / ".super-dev" / "WORKFLOW.md"
            summary_file = temp_project_dir / "output" / "bootstrap-demo-bootstrap.md"
            assert workflow_file.exists()
            assert summary_file.exists()
            assert "Required Pipeline Order" in workflow_file.read_text(encoding="utf-8")
            assert "How To Start" in summary_file.read_text(encoding="utf-8")
        finally:
            os.chdir(original_cwd)


class TestCLIConfig:
    """测试 config 命令"""

    def test_config_list(self, temp_project_dir: Path, sample_config):
        """测试列出配置"""
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            # 创建配置文件 (使用当前目录的 super-dev.yaml)
            config_data = {
                "name": sample_config.name,
                "platform": sample_config.platform,
                "frontend": sample_config.frontend,
                "backend": sample_config.backend
            }
            config_path = Path.cwd() / "super-dev.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            cli = SuperDevCLI()
            result = cli.run(["config", "list"])

            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_config_get(self, temp_project_dir: Path, sample_config):
        """测试获取配置"""
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            config_data = {
                "name": sample_config.name,
                "quality_gate": 85
            }
            config_path = Path.cwd() / "super-dev.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            cli = SuperDevCLI()
            result = cli.run(["config", "get", "quality_gate"])

            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_config_set(self, temp_project_dir: Path):
        """测试设置配置"""
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            config_data = {"name": "test"}
            config_path = Path.cwd() / "super-dev.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            cli = SuperDevCLI()
            result = cli.run(["config", "set", "quality_gate", "90"])

            assert result == 0

            # 验证配置已更新
            with open(config_path) as f:
                config = yaml.safe_load(f)
                assert config["quality_gate"] == 90
        finally:
            os.chdir(original_cwd)

    def test_config_set_unknown_key(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            config_path = Path.cwd() / "super-dev.yaml"
            with open(config_path, "w") as f:
                yaml.dump({"name": "test"}, f)

            cli = SuperDevCLI()
            result = cli.run(["config", "set", "unknown_key", "value"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_config_set_rejects_invalid_value(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)

        try:
            config_path = Path.cwd() / "super-dev.yaml"
            with open(config_path, "w") as f:
                yaml.dump({"name": "test"}, f)

            cli = SuperDevCLI()
            result = cli.run(["config", "set", "host_compatibility_min_score", "120"])
            assert result == 1
        finally:
            os.chdir(original_cwd)


class TestCLIExpert:
    """测试 expert 命令"""

    def test_expert_pm(self, temp_project_dir: Path):
        """测试调用 PM 专家"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["expert", "PM", "帮我分析需求"])
            assert result == 0
            assert (temp_project_dir / "output" / "expert-pm-advice.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_expert_architect(self, temp_project_dir: Path):
        """测试调用架构师专家"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["expert", "ARCHITECT", "设计系统架构"])
            assert result == 0
            assert (temp_project_dir / "output" / "expert-architect-advice.md").exists()
        finally:
            os.chdir(original_cwd)


class TestCLIPreview:
    """测试 preview 命令"""

    def test_preview_generation(self, temp_project_dir: Path):
        """测试原型生成"""
        preview_path = temp_project_dir / "preview.html"
        cli = SuperDevCLI()
        result = cli.run([
            "preview",
            "-o", str(preview_path)
        ])

        assert result == 0
        assert preview_path.exists()


class TestCLIDeploy:
    """测试 deploy 命令"""

    def test_deploy_docker(self, temp_project_dir: Path):
        """测试生成 Dockerfile"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["deploy", "--docker"])
            assert result == 0
            assert (temp_project_dir / "Dockerfile").exists()
            assert (temp_project_dir / "k8s" / "deployment.yaml").exists()
        finally:
            os.chdir(original_cwd)

    def test_deploy_cicd_github(self, temp_project_dir: Path):
        """测试生成 GitHub Actions 配置"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["deploy", "--cicd", "github"])
            assert result == 0
            assert (temp_project_dir / ".github" / "workflows" / "ci.yml").exists()
            assert (temp_project_dir / ".github" / "workflows" / "cd.yml").exists()
        finally:
            os.chdir(original_cwd)

    def test_deploy_cicd_gitlab(self, temp_project_dir: Path):
        """测试生成 GitLab CI 配置"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["deploy", "--cicd", "gitlab"])
            assert result == 0
            assert (temp_project_dir / ".gitlab-ci.yml").exists()
        finally:
            os.chdir(original_cwd)

    def test_deploy_cicd_all_platforms(self, temp_project_dir: Path):
        """测试一次生成五大 CI/CD 平台配置"""
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["deploy", "--cicd", "all"])
            assert result == 0
            assert (temp_project_dir / ".github" / "workflows" / "ci.yml").exists()
            assert (temp_project_dir / ".github" / "workflows" / "cd.yml").exists()
            assert (temp_project_dir / ".gitlab-ci.yml").exists()
            assert (temp_project_dir / "Jenkinsfile").exists()
            assert (temp_project_dir / ".azure-pipelines.yml").exists()
            assert (temp_project_dir / "bitbucket-pipelines.yml").exists()
        finally:
            os.chdir(original_cwd)


class TestCLIReview:
    """测试 review docs 命令"""

    def test_review_docs_defaults_to_pending(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["review", "docs"])

            assert result == 0
            output = capsys.readouterr().out
            assert "三文档确认状态" in output
            assert "状态: 待确认" in output
            assert "document-confirmation.json" in output
        finally:
            os.chdir(original_cwd)

    def test_review_docs_json_persists_confirmation(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(
                [
                    "review",
                    "docs",
                    "--status",
                    "confirmed",
                    "--comment",
                    "文档已确认，可以进入 Spec 阶段",
                    "--run-id",
                    "run-123",
                    "--actor",
                    "tester",
                    "--json",
                ]
            )

            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert payload["status"] == "confirmed"
            assert payload["comment"] == "文档已确认，可以进入 Spec 阶段"
            assert payload["run_id"] == "run-123"
            assert payload["actor"] == "tester"
            assert payload["updated_at"]

            state_file = (
                temp_project_dir / ".super-dev" / "review-state" / "document-confirmation.json"
            )
            assert state_file.exists()
            persisted = json.loads(state_file.read_text(encoding="utf-8"))
            assert persisted["status"] == "confirmed"
            assert persisted["comment"] == "文档已确认，可以进入 Spec 阶段"
            assert persisted["run_id"] == "run-123"
            assert persisted["actor"] == "tester"
        finally:
            os.chdir(original_cwd)

    def test_review_ui_defaults_to_pending(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["review", "ui"])

            assert result == 0
            output = capsys.readouterr().out
            assert "UI 改版状态" in output
            assert "状态: 待确认" in output
            assert "ui-revision.json" in output
        finally:
            os.chdir(original_cwd)

    def test_review_ui_json_persists_revision_request(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(
                [
                    "review",
                    "ui",
                    "--status",
                    "revision_requested",
                    "--comment",
                    "Hero 太空，需要重做首屏",
                    "--run-id",
                    "run-ui-123",
                    "--actor",
                    "tester",
                    "--json",
                ]
            )

            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert payload["status"] == "revision_requested"
            assert payload["comment"] == "Hero 太空，需要重做首屏"
            assert payload["run_id"] == "run-ui-123"
            assert payload["actor"] == "tester"
            assert payload["updated_at"]

            state_file = temp_project_dir / ".super-dev" / "review-state" / "ui-revision.json"
            assert state_file.exists()
            persisted = json.loads(state_file.read_text(encoding="utf-8"))
            assert persisted["status"] == "revision_requested"
        finally:
            os.chdir(original_cwd)

    def test_review_architecture_defaults_to_pending(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["review", "architecture"])

            assert result == 0
            output = capsys.readouterr().out
            assert "架构返工状态" in output
            assert "状态: 待确认" in output
            assert "architecture-revision.json" in output
        finally:
            os.chdir(original_cwd)

    def test_review_quality_json_persists_revision_request(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(
                [
                    "review",
                    "quality",
                    "--status",
                    "revision_requested",
                    "--comment",
                    "质量门禁未通过，需要修复安全和质量问题",
                    "--run-id",
                    "run-quality-123",
                    "--actor",
                    "tester",
                    "--json",
                ]
            )

            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert payload["status"] == "revision_requested"
            assert payload["comment"] == "质量门禁未通过，需要修复安全和质量问题"
            state_file = temp_project_dir / ".super-dev" / "review-state" / "quality-revision.json"
            assert state_file.exists()
        finally:
            os.chdir(original_cwd)

    def test_deploy_rehearsal_docs(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["deploy", "--cicd", "github", "--rehearsal"])
            assert result == 0
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-launch-rehearsal.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rollback-playbook.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-smoke-checklist.md"))
        finally:
            os.chdir(original_cwd)

    def test_deploy_rehearsal_verify_generates_report(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            project_name = "my-project"
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            (output_dir / f"{project_name}-redteam.md").write_text(
                "- **Critical 问题**: 0\n**状态**: 通过 - 质量良好\n",
                encoding="utf-8",
            )
            (output_dir / f"{project_name}-quality-gate.md").write_text(
                "**状态**: <span style='color:green'>通过</span>\n**总分**: 90/100\n",
                encoding="utf-8",
            )
            (output_dir / f"{project_name}-pipeline-metrics.json").write_text(
                '{"project_name":"demo","success":true,"success_rate":100,"stages":[]}',
                encoding="utf-8",
            )
            delivery_dir = output_dir / "delivery"
            delivery_dir.mkdir(parents=True, exist_ok=True)
            (delivery_dir / f"{project_name}-delivery-manifest.json").write_text(
                '{"project_name":"demo","status":"ready"}',
                encoding="utf-8",
            )
            (temp_project_dir / "backend" / "migrations").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "backend" / "migrations" / "001_init.sql").write_text("-- migration", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["deploy", "--cicd", "github", "--rehearsal", "--rehearsal-verify"])
            assert result == 0
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rehearsal-report.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rehearsal-report.json"))
        finally:
            os.chdir(original_cwd)


class TestCLIQuality:
    """测试 quality 命令"""

    def test_quality_document_check(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "demo-prd.md").write_text("# PRD", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["quality", "--type", "prd"])
            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_quality_all_generates_report(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["quality", "--type", "all"])
            assert result in (0, 1)
            assert any((temp_project_dir / "output").glob("*-quality-gate.md"))
            assert any((temp_project_dir / "output").glob("*-ui-review.md"))
            assert any((temp_project_dir / "output").glob("*-ui-review.json"))
        finally:
            os.chdir(original_cwd)

    def test_quality_ui_review_generates_report(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "demo-uiux.md").write_text(
                "# demo\n\n## 设计 Intelligence 结论\n\n## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["quality", "--type", "ui-review"])
            assert result in (0, 1)
            assert any((temp_project_dir / "output").glob("*-ui-review.md"))
            assert any((temp_project_dir / "output").glob("*-ui-review.json"))
        finally:
            os.chdir(original_cwd)


class TestCLIDesign:
    """测试 design 命令关键分支"""

    def test_design_tokens_json_and_tailwind(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            json_path = temp_project_dir / "tokens.json"
            tailwind_path = temp_project_dir / "tailwind.json"

            json_result = cli.run(
                ["design", "tokens", "--primary", "#3B82F6", "--format", "json", "--output", str(json_path)]
            )
            tailwind_result = cli.run(
                ["design", "tokens", "--primary", "#3B82F6", "--format", "tailwind", "--output", str(tailwind_path)]
            )

            assert json_result == 0
            assert tailwind_result == 0
            assert json_path.exists()
            assert tailwind_path.exists()
        finally:
            os.chdir(original_cwd)


class TestCLISkillAndIntegrate:
    """测试 skill 和 integrate 命令"""

    def test_skill_targets(self):
        cli = SuperDevCLI()
        result = cli.run(["skill", "targets"])
        assert result == 0

    def test_integrate_setup_qoder(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "setup", "--target", "qoder", "--force"])
            assert result == 0
            assert (temp_project_dir / ".qoder" / "rules.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_integrate_setup_antigravity(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "setup", "--target", "antigravity", "--force"])
            assert result == 0
            assert (temp_project_dir / "GEMINI.md").exists()
            assert (temp_project_dir / ".agent" / "workflows" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_integrate_matrix_text(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "matrix", "--target", "codex-cli"])
            assert result == 0
            output = capsys.readouterr().out
            assert "codex-cli" in output
            assert "适配模式" in output
            assert "使用模式" in output
            assert "触发命令" in output
            assert "官方文档" in output
        finally:
            os.chdir(original_cwd)

    def test_integrate_matrix_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "matrix", "--target", "qoder", "--json"])
            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert isinstance(payload, dict)
            assert "profiles" in payload
            assert "docs_checks" in payload
            assert len(payload["profiles"]) == 1
            row = payload["profiles"][0]
            assert row["host"] == "qoder"
            assert row["adapter_mode"] == "native-ide-rule-file"
            assert "official_docs_url" in row
        finally:
            os.chdir(original_cwd)

    def test_integrate_harden_json(self, temp_project_dir: Path, capsys, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "harden", "--target", "codex-cli", "--json"])
            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert isinstance(payload, dict)
            assert payload["selected_targets"] == ["codex-cli"]
            assert "hardening_results" in payload
            item = payload["hardening_results"]["codex-cli"]
            assert item["plan"]["trigger_mode"] == "text"
            assert "skill_install" in item
            assert "official_compare" in item
            assert "compatibility" in payload
            assert "official_compare_summary" in payload
            assert "host_parity_summary" in payload
            assert "host_gate_summary" in payload
            assert "host_runtime_script_summary" in payload
            assert "host_recovery_summary" in payload
            assert "host_parity_index" in payload
            assert payload["host_parity_summary"]["total"] == 1
            assert payload["host_gate_summary"]["total"] == 1
            assert payload["host_runtime_script_summary"]["total"] == 1
            assert payload["host_recovery_summary"]["total"] == 1
            assert payload["host_parity_index"]["passed"] is True
            gate = payload["host_gate_summary"]["hosts"]["codex-cli"]
            assert gate["passed"] is True
            runtime_script = payload["host_runtime_script_summary"]["hosts"]["codex-cli"]
            assert runtime_script["passed"] is True
            recovery = payload["host_recovery_summary"]["hosts"]["codex-cli"]
            assert recovery["passed"] is True
            assert any("integrate setup --target codex-cli --force" in cmd for cmd in recovery["recommended_commands"])
            assert "report_files" in payload
            assert Path(payload["report_files"]["onepage_markdown"]).exists()
            assert Path(payload["report_files"]["history_onepage_markdown"]).exists()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.parametrize(
        "target, expected_file",
        [(name, config.files[0]) for name, config in IntegrationManager.TARGETS.items()],
    )
    def test_integrate_setup_each_target(self, temp_project_dir: Path, target: str, expected_file: str):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "setup", "--target", target, "--force"])
            assert result == 0
            assert (temp_project_dir / expected_file).exists()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.parametrize(
        "target",
        list(SkillManager.TARGET_PATHS.keys()),
    )
    def test_skill_builtin_install_each_target(self, temp_project_dir: Path, target: str, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            install_result = cli.run(
                ["skill", "install", "super-dev", "--target", target, "--name", "super-dev-core", "--force"]
            )
            assert install_result == 0

            list_result = cli.run(["skill", "list", "--target", target])
            assert list_result == 0

            uninstall_result = cli.run(["skill", "uninstall", "super-dev-core", "--target", target])
            assert uninstall_result == 0
        finally:
            os.chdir(original_cwd)

    def test_onboard_single_host_installs_all_components(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "claude-code", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".claude" / "CLAUDE.md").exists()
            assert (temp_project_dir / ".claude" / "agents" / "super-dev-core.md").exists()
            assert (fake_home / ".claude" / "agents" / "super-dev-core.md").exists()
            assert (temp_project_dir / ".claude" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_antigravity_installs_project_global_and_skill(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "antigravity", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / "GEMINI.md").exists()
            assert (temp_project_dir / ".agent" / "workflows" / "super-dev.md").exists()
            assert (temp_project_dir / ".gemini" / "commands" / "super-dev.md").exists()
            assert (fake_home / ".gemini" / "GEMINI.md").exists()
            assert (fake_home / ".gemini" / "commands" / "super-dev.md").exists()
            assert (fake_home / ".gemini" / "skills" / "super-dev-core" / "SKILL.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_trae_installs_project_rules_and_host_skill(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".trae").mkdir(parents=True, exist_ok=True)
        (fake_home / ".trae" / "skills").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "trae", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".trae" / "project_rules.md").exists()
            assert (temp_project_dir / ".trae" / "rules.md").exists()
            assert (fake_home / ".trae" / "user_rules.md").exists()
            assert (fake_home / ".trae" / "rules.md").exists()
            assert (fake_home / ".trae" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".trae" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_trae_skips_compat_skill_when_surface_missing(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "trae", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".trae" / "project_rules.md").exists()
            assert (temp_project_dir / ".trae" / "rules.md").exists()
            assert (fake_home / ".trae" / "user_rules.md").exists()
            assert (fake_home / ".trae" / "rules.md").exists()
            assert not (fake_home / ".trae" / "skills" / "super-dev-core" / "SKILL.md").exists()
            output = capsys.readouterr().out
            assert "未检测到官方或兼容 Skill 目录" in output
        finally:
            os.chdir(original_cwd)

    def test_onboard_codex_cli_skips_slash_mapping(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / "AGENTS.md").exists()
            assert (fake_home / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_codex_cli_preserves_existing_root_agents(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        agents = temp_project_dir / "AGENTS.md"
        agents.write_text("# Existing Project Rules\n\n- Keep current behavior.\n", encoding="utf-8")
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert result == 0
            content = agents.read_text(encoding="utf-8")
            assert "# Existing Project Rules" in content
            assert "BEGIN SUPER DEV CODEX" in content
            assert "super-dev:" in content
        finally:
            os.chdir(original_cwd)

    def test_onboard_kiro_installs_global_steering(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "kiro", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".kiro" / "steering" / "super-dev.md").exists()
            assert (fake_home / ".kiro" / "steering" / "AGENTS.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_prints_host_specific_next_steps(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "kimi-cli", "--force", "--yes"])
            assert result == 0

            output = capsys.readouterr().out
            assert "接下来这样用" in output
            assert "kimi-cli: 打开宿主后输入 super-dev: 你的需求" in output
        finally:
            os.chdir(original_cwd)

    def test_onboard_yes_defaults_to_all_targets(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--yes", "--force", "--skip-skill"])
            assert result == 0
            assert (temp_project_dir / "GEMINI.md").exists()
            assert (temp_project_dir / ".agent" / "workflows" / "super-dev.md").exists()
            assert (temp_project_dir / ".gemini" / "commands" / "super-dev.md").exists()
            assert (temp_project_dir / ".claude" / "CLAUDE.md").exists()
            assert (temp_project_dir / "AGENTS.md").exists()
            assert (temp_project_dir / ".qoder" / "rules.md").exists()
            assert (temp_project_dir / ".qoder" / "commands" / "super-dev.md").exists()
            assert (temp_project_dir / ".claude" / "commands" / "super-dev.md").exists()
            assert (temp_project_dir / ".github" / "copilot-instructions.md").exists()
            assert (temp_project_dir / ".cursor" / "rules" / "super-dev.mdc").exists()
            assert not (temp_project_dir / ".kimi" / "commands" / "super-dev.md").exists()
            assert not (temp_project_dir / ".kimi" / "AGENTS.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_detect_host_targets_uses_windows_env_candidates(self, temp_project_dir: Path, monkeypatch):
        localapp = temp_project_dir / "LocalAppData"
        target = localapp / "Programs" / "Trae" / "Trae.exe"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        monkeypatch.setenv("LOCALAPPDATA", str(localapp))

        cli = SuperDevCLI()
        detected, details = cli._detect_host_targets(available_targets=["trae"])
        assert detected == ["trae"]
        assert any(item.startswith("path:") for item in details["trae"])

    def test_onboard_auto_detects_targets_from_path(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            codex_cmd = bin_dir / "codex"
            codex_cmd.write_text("#!/usr/bin/env sh\necho codex\n", encoding="utf-8")
            codex_cmd.chmod(0o755)
            os.environ["PATH"] = str(bin_dir)

            cli = SuperDevCLI()
            result = cli.run(["onboard", "--auto", "--yes", "--force"])
            assert result == 0
            assert (temp_project_dir / "AGENTS.md").exists()
            assert (fake_home / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_doctor_reports_not_ready_then_ready(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            before = cli.run(["doctor", "--host", "claude-code"])
            assert before == 1

            onboard = cli.run(["onboard", "--host", "claude-code", "--force", "--yes"])
            assert onboard == 0

            after = cli.run(["doctor", "--host", "claude-code"])
            assert after == 0
        finally:
            os.chdir(original_cwd)

    def test_doctor_prints_usage_guidance_for_codex_cli(self, temp_project_dir: Path, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        original_home = os.environ.get("HOME")
        os.environ["HOME"] = str(fake_home)
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["doctor", "--host", "codex-cli", "--repair", "--force"])
            assert result == 0

            output = capsys.readouterr().out
            assert "主入口" in output
            assert "super-dev: <需求描述>" in output
            assert "使用模式: agents-and-skill" in output
            assert "触发位置" in output
            assert "接入后重启: 是" in output
            assert "Smoke 验收语句" in output
            assert "SMOKE_OK" in output
        finally:
            if original_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = original_home
            os.chdir(original_cwd)

    def test_doctor_prints_host_preconditions_for_iflow(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["doctor", "--host", "iflow", "--repair", "--force"])
            assert result == 0

            output = capsys.readouterr().out
            assert "宿主前置条件" in output
            assert "需宿主鉴权" in output or "已检测到鉴权配置" in output
            assert "/auth" in output
            assert "IFLOW_API_KEY" in output
            assert "Invalid API key provided" in output
        finally:
            os.chdir(original_cwd)

    def test_doctor_prints_multiple_host_precondition_items_for_codex(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["doctor", "--host", "codex-cli", "--repair", "--force"])
            assert result == 0

            output = capsys.readouterr().out
            assert "宿主前置条件" in output
            assert "接入后需重开宿主会话" in output
            assert "需在目标项目/工作区内触发" in output
            assert "关闭旧会话并新开一个宿主会话" in output
        finally:
            os.chdir(original_cwd)

    def test_doctor_accepts_global_slash_mapping_when_project_slash_missing(
        self,
        temp_project_dir: Path,
        monkeypatch,
    ):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            fake_home = temp_project_dir / "fake-home"
            fake_home.mkdir(parents=True, exist_ok=True)
            monkeypatch.setenv("HOME", str(fake_home))

            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "claude-code", "--force", "--yes"])
            assert onboard == 0

            project_slash = temp_project_dir / ".claude" / "commands" / "super-dev.md"
            assert project_slash.exists()
            project_slash.unlink()

            global_slash = fake_home / ".claude" / "commands" / "super-dev.md"
            assert global_slash.exists()

            result = cli.run(["doctor", "--host", "claude-code"])
            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_doctor_repair_fixes_host_issues(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            before = cli.run(["doctor", "--host", "codex-cli"])
            assert before == 1

            repaired = cli.run(["doctor", "--host", "codex-cli", "--repair", "--force"])
            assert repaired == 0

            assert (temp_project_dir / "AGENTS.md").exists()
            assert (fake_home / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_doctor_flags_stale_contract_content(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "claude-code", "--force", "--yes"])
            assert onboard == 0

            stale_file = temp_project_dir / ".claude" / "commands" / "super-dev.md"
            stale_file.write_text("# stale\n/super-dev\n", encoding="utf-8")

            result = cli.run(["doctor", "--host", "claude-code"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_detect_json_outputs_compatibility_summary(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            codex_cmd = bin_dir / "codex"
            codex_cmd.write_text("#!/usr/bin/env sh\necho codex\n", encoding="utf-8")
            codex_cmd.chmod(0o755)
            os.environ["PATH"] = str(bin_dir)

            cli = SuperDevCLI()
            result = cli.run(["detect", "--json", "--auto"])
            assert result == 0

            out = capsys.readouterr().out
            payload = json.loads(out)
            assert "detected_hosts" in payload
            assert "selected_targets" in payload
            assert "compatibility" in payload
            assert "codex-cli" in payload["detected_hosts"]
            assert payload["compatibility"]["total_hosts"] >= 1
            assert "flow_consistent_hosts" in payload["compatibility"]
            assert "flow_consistency_score" in payload["compatibility"]
            assert payload["usage_profiles"]["codex-cli"]["usage_mode"] == "agents-and-skill"
            assert payload["usage_profiles"]["codex-cli"]["certification_level"] == "certified"
            assert payload["usage_profiles"]["codex-cli"]["certification_label"] == "Certified"
            assert payload["usage_profiles"]["codex-cli"]["trigger_command"] == "super-dev: <需求描述>"
            assert payload["usage_profiles"]["codex-cli"]["final_trigger"] == "super-dev: 你的需求"
            assert payload["usage_profiles"]["codex-cli"]["host_protocol_mode"] == "official-skill"
            assert payload["usage_profiles"]["codex-cli"]["host_protocol_summary"] == "官方 AGENTS.md + 官方 Skills"
            assert "SMOKE_OK" in payload["usage_profiles"]["codex-cli"]["smoke_test_prompt"]
            assert payload["usage_profiles"]["codex-cli"]["smoke_test_steps"]
            assert payload["report"]["hosts"]["codex-cli"]["usage_profile"]["requires_restart_after_onboard"] is True
            assert payload["report"]["hosts"]["codex-cli"]["usage_profile"]["certification_reason"]
            assert "report_files" in payload
            report_files = payload["report_files"]
            assert Path(report_files["json"]).exists()
            assert Path(report_files["markdown"]).exists()
            assert Path(report_files["history_json"]).exists()
            assert Path(report_files["history_markdown"]).exists()
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_detect_no_save_skips_report_files(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            codex_cmd = bin_dir / "codex"
            codex_cmd.write_text("#!/usr/bin/env sh\necho codex\n", encoding="utf-8")
            codex_cmd.chmod(0o755)
            os.environ["PATH"] = str(bin_dir)

            cli = SuperDevCLI()
            result = cli.run(["detect", "--json", "--no-save"])
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert "report_files" not in payload
            assert not any((temp_project_dir / "output").glob("*-host-compatibility.json"))
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_detect_save_profile_updates_super_dev_yaml(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            codex_cmd = bin_dir / "codex"
            codex_cmd.write_text("#!/usr/bin/env sh\necho codex\n", encoding="utf-8")
            codex_cmd.chmod(0o755)
            os.environ["PATH"] = str(bin_dir)

            cli = SuperDevCLI()
            result = cli.run(["detect", "--json", "--save-profile", "--auto"])
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert payload.get("host_profile_updated") is True

            config_file = temp_project_dir / "super-dev.yaml"
            assert config_file.exists()
            config_data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
            assert config_data.get("host_profile_enforce_selected") is True
            assert "codex-cli" in config_data.get("host_profile_targets", [])
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_detect_prints_usage_guidance_for_detected_host(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            codex_cmd = bin_dir / "codex"
            codex_cmd.write_text("#!/usr/bin/env sh\necho codex\n", encoding="utf-8")
            codex_cmd.chmod(0o755)
            os.environ["PATH"] = str(bin_dir)

            cli = SuperDevCLI()
            result = cli.run(["detect", "--auto", "--no-save"])
            assert result == 0

            output = capsys.readouterr().out
            assert "主入口" in output
            assert "宿主协议: 官方 AGENTS.md + 官方 Skills (official-skill)" in output
            assert "触发命令: super-dev: <需求描述>" in output
            assert "触发位置" in output
            assert "接入后重启: 是" in output
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_integrate_smoke_outputs_codex_acceptance(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "smoke", "--target", "codex-cli"])
            assert result == 0

            output = capsys.readouterr().out
            assert "Super Dev 宿主 Smoke 验收" in output
            assert "codex-cli" in output
            assert "SMOKE_OK" in output
            assert "最终输入: super-dev: 你的需求" in output
        finally:
            os.chdir(original_cwd)

    def test_integrate_audit_flags_stale_surface(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert onboard == 0
            capsys.readouterr()

            agents_file = temp_project_dir / "AGENTS.md"
            agents_file.write_text("# stale\nsuper-dev:\n", encoding="utf-8")

            result = cli.run(["integrate", "audit", "--target", "codex-cli"])
            assert result == 1

            output = capsys.readouterr().out
            assert "Super Dev 宿主 Surface 审计" in output
            assert "codex-cli" in output
            assert "过期/缺失的接入面" in output
            assert "project:AGENTS.md" in output
        finally:
            os.chdir(original_cwd)

    def test_integrate_audit_json_repairs_and_writes_report(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "audit", "--target", "codex-cli", "--repair", "--force", "--json"])
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert payload["report"]["overall_ready"] is True
            assert payload["compatibility"]["hosts"]["codex-cli"]["ready"] is True
            assert payload["usage_profiles"]["codex-cli"]["final_trigger"] == "super-dev: 你的需求"
            assert payload["report_files"]["json"].endswith("-host-surface-audit.json")
            assert Path(payload["report_files"]["json"]).exists()
            assert Path(payload["report_files"]["markdown"]).exists()
        finally:
            os.chdir(original_cwd)

    def test_integrate_audit_repair_refreshes_stale_contract_content(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert onboard == 0
            capsys.readouterr()

            agents_file = temp_project_dir / "AGENTS.md"
            agents_file.write_text("# stale\nsuper-dev:\n", encoding="utf-8")

            result = cli.run(["integrate", "audit", "--target", "codex-cli", "--repair", "--force", "--json"])
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert payload["report"]["hosts"]["codex-cli"]["ready"] is True
            refreshed = agents_file.read_text(encoding="utf-8")
            assert "research" in refreshed
            assert "output/*-prd.md" in refreshed
        finally:
            os.chdir(original_cwd)

    def test_integrate_validate_json_emits_runtime_matrix(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert onboard == 0
            capsys.readouterr()

            result = cli.run(["integrate", "validate", "--target", "codex-cli", "--json"])
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert payload["selected_targets"] == ["codex-cli"]
            assert payload["report_files"]["json"].endswith("-host-runtime-validation.json")
            assert Path(payload["report_files"]["json"]).exists()
            assert Path(payload["report_files"]["markdown"]).exists()
            assert len(payload["hosts"]) == 1
            host = payload["hosts"][0]
            assert host["host"] == "codex-cli"
            assert host["surface_ready"] is True
            assert host["final_trigger"] == "super-dev: 你的需求"
            assert host["host_protocol_summary"] == "官方 AGENTS.md + 官方 Skills"
            assert host["manual_runtime_status"] == "pending"
            assert host["runtime_checklist"]
            assert host["pass_criteria"]
        finally:
            os.chdir(original_cwd)

    def test_integrate_validate_status_roundtrip(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "codex-cli", "--force", "--yes"])
            assert onboard == 0
            capsys.readouterr()

            result = cli.run(
                [
                    "integrate",
                    "validate",
                    "--target",
                    "codex-cli",
                    "--status",
                    "passed",
                    "--comment",
                    "首轮先进入 research，三文档已真实落盘",
                    "--json",
                ]
            )
            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            assert payload["manual_runtime_status"] == "passed"
            assert payload["manual_runtime_status_label"] == "已真人通过"

            result = cli.run(["integrate", "validate", "--target", "codex-cli", "--json"])
            assert result == 0
            payload = json.loads(capsys.readouterr().out)
            host = payload["hosts"][0]
            assert host["manual_runtime_status"] == "passed"
            assert host["manual_runtime_status_label"] == "已真人通过"
            assert host["manual_runtime_comment"] == "首轮先进入 research，三文档已真实落盘"
        finally:
            os.chdir(original_cwd)

    def test_integrate_validate_text_writes_runtime_matrix_report(self, temp_project_dir: Path, monkeypatch, capsys):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".trae").mkdir(parents=True, exist_ok=True)
        (fake_home / ".trae" / "skills").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            onboard = cli.run(["onboard", "--host", "trae", "--force", "--yes"])
            assert onboard == 0
            capsys.readouterr()

            result = cli.run(["integrate", "validate", "--target", "trae"])
            assert result == 0

            output = capsys.readouterr().out
            assert "Super Dev 宿主运行时验收矩阵" in output
            assert "trae" in output
            assert "运行时检查清单" in output
            assert "通过标准" in output
            assert "验收矩阵报告" in output

            json_reports = list((temp_project_dir / "output").glob("*-host-runtime-validation.json"))
            md_reports = list((temp_project_dir / "output").glob("*-host-runtime-validation.md"))
            assert json_reports
            assert md_reports
        finally:
            os.chdir(original_cwd)

    def test_start_json_prefers_certified_slash_host(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        original_path = os.environ.get("PATH", "")
        os.chdir(temp_project_dir)
        try:
            bin_dir = temp_project_dir / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("claude", "codex"):
                cmd_file = bin_dir / command
                cmd_file.write_text("#!/usr/bin/env sh\necho host\n", encoding="utf-8")
                cmd_file.chmod(0o755)
            os.environ["PATH"] = f"{bin_dir}:{original_path}"

            cli = SuperDevCLI()
            result = cli.run(
                [
                    "start",
                    "--json",
                    "--skip-onboard",
                    "--idea",
                    "做一个商业级官网",
                ]
            )
            assert result == 0

            payload = json.loads(capsys.readouterr().out)
            assert payload["selected_host"] == "claude-code"
            assert payload["usage_profile"]["certification_level"] == "certified"
            assert payload["usage_profile"]["host_protocol_mode"] == "official-subagent"
            assert payload["usage_profile"]["host_protocol_summary"] == "官方 commands + subagents"
            assert payload["usage_profile"]["final_trigger"] == '/super-dev "你的需求"'
            assert payload["recommended_trigger"].startswith('/super-dev "')

            config_data = yaml.safe_load((temp_project_dir / "super-dev.yaml").read_text(encoding="utf-8"))
            assert config_data["host_profile_targets"] == ["claude-code"]
            assert config_data["host_profile_enforce_selected"] is True
        finally:
            os.environ["PATH"] = original_path
            os.chdir(original_cwd)

    def test_start_json_reports_recommended_hosts_when_none_detected(self, temp_project_dir: Path, capsys, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            monkeypatch.setenv("PATH", str(temp_project_dir / "empty-bin"))
            monkeypatch.setattr(
                cli_module,
                "host_path_candidates",
                lambda _target: [],
            )
            cli = SuperDevCLI()
            result = cli.run(["start", "--json", "--skip-onboard"])
            assert result == 1

            payload = json.loads(capsys.readouterr().out)
            assert payload["status"] == "error"
            assert payload["reason"] == "no-host-detected"
            recommended_ids = {item["id"] for item in payload["recommended_hosts"]}
            assert {"claude-code", "codex-cli"}.issubset(recommended_ids)
        finally:
            os.chdir(original_cwd)

    def test_update_check_reports_latest_version(self, capsys, monkeypatch):
        cli = SuperDevCLI()

        class DummyResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"info": {"version": "2.1.1"}}

        monkeypatch.setattr("super_dev.cli.requests.get", lambda *args, **kwargs: DummyResponse())

        result = cli.run(["update", "--check"])
        assert result == 0
        output = capsys.readouterr().out
        assert "当前版本" in output
        assert "PyPI 最新版本" in output
        assert "2.1.1" in output

    def test_update_uses_uv_when_requested(self, capsys, monkeypatch):
        cli = SuperDevCLI()
        calls: list[list[str]] = []

        class DummyResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"info": {"version": "2.1.1"}}

        monkeypatch.setattr("super_dev.cli.requests.get", lambda *args, **kwargs: DummyResponse())

        def fake_run(command, check=False):
            calls.append(command)
            return SimpleNamespace(returncode=0)

        monkeypatch.setattr("super_dev.cli.subprocess.run", fake_run)

        result = cli.run(["update", "--method", "uv"])
        assert result == 0
        assert calls == [["uv", "tool", "upgrade", "super-dev"]]
        output = capsys.readouterr().out
        assert "升级方式" in output
        assert "uv" in output

    def test_update_uses_pip_when_requested(self, capsys, monkeypatch):
        cli = SuperDevCLI()
        calls: list[list[str]] = []

        class DummyResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"info": {"version": "2.1.1"}}

        monkeypatch.setattr("super_dev.cli.requests.get", lambda *args, **kwargs: DummyResponse())

        def fake_run(command, check=False):
            calls.append(command)
            return SimpleNamespace(returncode=0)

        monkeypatch.setattr("super_dev.cli.subprocess.run", fake_run)

        result = cli.run(["update", "--method", "pip"])
        assert result == 0
        assert calls == [[os.sys.executable, "-m", "pip", "install", "-U", "super-dev"]]

    def test_policy_init_and_show(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            presets_result = cli.run(["policy", "presets"])
            assert presets_result == 0

            init_result = cli.run(["policy", "init", "--preset", "enterprise"])
            assert init_result == 0
            policy_file = temp_project_dir / ".super-dev" / "policy.yaml"
            assert policy_file.exists()

            show_result = cli.run(["policy", "show"])
            assert show_result == 0
            output = capsys.readouterr().out
            assert "红队审查: 开启" in output
            assert "最低质量阈值: 85" in output
            assert "关键宿主列表: 未配置" in output
            assert "关键宿主就绪校验: 关闭" in output
        finally:
            os.chdir(original_cwd)

    def test_setup_host_runs_onboard_and_doctor(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["setup", "--host", "codex-cli", "--force"])
            assert result == 0
            assert (temp_project_dir / "AGENTS.md").exists()
            assert (fake_home / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_install_host_runs_setup_flow(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        (fake_home / ".codex").mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["install", "--host", "codex-cli", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / "AGENTS.md").exists()
            assert (fake_home / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert not (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)


class TestCLITask:
    """测试 task 命令"""

    def test_task_run_status_and_list(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            changes_dir = temp_project_dir / ".super-dev" / "changes" / "demo-change"
            changes_dir.mkdir(parents=True, exist_ok=True)
            (changes_dir / "change.yaml").write_text(
                (
                    "id: demo-change\n"
                    "title: Demo Change\n"
                    "status: proposed\n"
                    "created_at: 2026-03-02T00:00:00\n"
                    "updated_at: 2026-03-02T00:00:00\n"
                ),
                encoding="utf-8",
            )
            (changes_dir / "tasks.md").write_text(
                (
                    "# Tasks\n\n"
                    "## 1. Frontend\n\n"
                    "- [ ] **1.1: 实现 auth 前端模块**\n\n"
                    "## 2. Backend\n\n"
                    "- [ ] **2.1: 实现 auth 后端能力**\n\n"
                    "## 4. Testing\n\n"
                    "- [ ] **4.1: 执行质量门禁前检查**\n"
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            run_result = cli.run(["task", "run", "demo-change", "--backend", "python"])
            assert run_result == 0
            assert (temp_project_dir / "output" / "demo-change-task-execution.md").exists()

            status_result = cli.run(["task", "status", "demo-change"])
            assert status_result == 0

            list_result = cli.run(["task", "list"])
            assert list_result == 0
        finally:
            os.chdir(original_cwd)


class TestCLIPipeline:
    """测试完整流水线关键产物"""

    def test_repo_map_command_generates_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "billing.py").write_text(
                "class BillingService:\n    pass\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["repo-map"])

            assert result == 0
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-repo-map.md").exists()
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-repo-map.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_repo_map_json_output_is_strict_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["repo-map", "--json"])
            captured = capsys.readouterr()

            assert result == 0
            payload = json.loads(captured.out)
            assert payload["project_name"] == temp_project_dir.name
        finally:
            os.chdir(original_cwd)

    def test_impact_command_generates_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "auth.py").write_text(
                "class AuthService:\n    def login(self):\n        return True\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["impact", "修改登录流程", "--files", "services/auth.py"])

            assert result == 0
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-impact-analysis.md").exists()
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-impact-analysis.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_feature_checklist_command_generates_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{temp_project_dir.name}-prd.md").write_text(
                "\n".join(
                    [
                        "# PRD",
                        "",
                        "## 2. 功能范围",
                        "",
                        "### 用户登录",
                        "- 支持邮箱密码登录",
                    ]
                ),
                encoding="utf-8",
            )
            change_dir = temp_project_dir / ".super-dev" / "changes" / "demo-change"
            change_dir.mkdir(parents=True, exist_ok=True)
            (change_dir / "tasks.md").write_text("# Tasks\n\n- [x] 用户登录\n", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["feature-checklist"])

            assert result == 0
            assert (output_dir / f"{temp_project_dir.name}-feature-checklist.md").exists()
            assert (output_dir / f"{temp_project_dir.name}-feature-checklist.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_feature_checklist_json_output_is_strict_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / f"{temp_project_dir.name}-prd.md").write_text(
                "\n".join(
                    [
                        "# PRD",
                        "",
                        "## 2. 功能范围",
                        "",
                        "### 用户登录",
                        "- 支持邮箱密码登录",
                    ]
                ),
                encoding="utf-8",
            )
            change_dir = temp_project_dir / ".super-dev" / "changes" / "demo-change"
            change_dir.mkdir(parents=True, exist_ok=True)
            (change_dir / "tasks.md").write_text("# Tasks\n\n- [x] 用户登录\n", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["feature-checklist", "--json"])
            captured = capsys.readouterr()

            assert result == 0
            payload = json.loads(captured.out)
            assert payload["project_name"] == temp_project_dir.name
            assert payload["status"] in {"ready", "partial", "unknown"}
        finally:
            os.chdir(original_cwd)

    def test_impact_json_output_is_strict_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "auth.py").write_text(
                "class AuthService:\n    def login(self):\n        return True\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["impact", "修改登录流程", "--files", "services/auth.py", "--json"])
            captured = capsys.readouterr()

            assert result == 0
            payload = json.loads(captured.out)
            assert payload["project_name"] == temp_project_dir.name
            assert payload["risk_level"] in {"low", "medium", "high"}
        finally:
            os.chdir(original_cwd)

    def test_regression_guard_command_generates_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "auth.py").write_text(
                "class AuthService:\n    def login(self):\n        return True\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["regression-guard", "修改登录流程", "--files", "services/auth.py"])

            assert result == 0
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-regression-guard.md").exists()
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-regression-guard.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_regression_guard_json_output_is_strict_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "auth.py").write_text(
                "class AuthService:\n    def login(self):\n        return True\n",
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["regression-guard", "修改登录流程", "--files", "services/auth.py", "--json"])
            captured = capsys.readouterr()

            assert result == 0
            payload = json.loads(captured.out)
            assert payload["project_name"] == temp_project_dir.name
            assert "high_priority_checks" in payload
        finally:
            os.chdir(original_cwd)

    def test_dependency_graph_command_generates_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "main.py").write_text("from services.auth import login\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "__init__.py").write_text("", encoding="utf-8")
            (temp_project_dir / "services" / "auth.py").write_text(
                "from api.routes import login_route\n\ndef login():\n    return login_route()\n",
                encoding="utf-8",
            )
            (temp_project_dir / "api").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "api" / "__init__.py").write_text("", encoding="utf-8")
            (temp_project_dir / "api" / "routes.py").write_text("def login_route():\n    return True\n", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["dependency-graph"])

            assert result == 0
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-dependency-graph.md").exists()
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-dependency-graph.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_dependency_graph_json_output_is_strict_json(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (temp_project_dir / "main.py").write_text("from services.auth import login\n", encoding="utf-8")
            (temp_project_dir / "services").mkdir(parents=True, exist_ok=True)
            (temp_project_dir / "services" / "__init__.py").write_text("", encoding="utf-8")
            (temp_project_dir / "services" / "auth.py").write_text("def login():\n    return True\n", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["dependency-graph", "--json"])
            captured = capsys.readouterr()

            assert result == 0
            payload = json.loads(captured.out)
            assert payload["project_name"] == temp_project_dir.name
            assert payload["node_count"] >= 1
        finally:
            os.chdir(original_cwd)

    def test_no_args_enters_install_guide(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            called: dict[str, bool] = {"value": False}

            def fake_cmd_install(args):
                called["value"] = True
                return 0

            monkeypatch.setattr(cli, "_cmd_install", fake_cmd_install)
            assert cli.run([]) == 0
            assert called["value"] is True
        finally:
            os.chdir(original_cwd)

    def test_install_command_renders_intro_then_runs_setup(self, temp_project_dir: Path, capsys, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()

            def fake_cmd_setup(args):
                return 0

            monkeypatch.setattr(cli, "_cmd_setup", fake_cmd_setup)
            result = cli.run(["install", "--host", "claude-code", "--yes"])
            assert result == 0
            output = capsys.readouterr().out
            assert "Super Dev 安装入口" in output
            assert "/super-dev 你的需求" in output
            assert "super-dev:" in output
            assert "text 宿主" in output
        finally:
            os.chdir(original_cwd)

    def test_spec_init_also_writes_bootstrap_artifacts(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            (temp_project_dir / "super-dev.yaml").write_text(
                yaml.safe_dump(
                    {
                        "name": "demo",
                        "platform": "web",
                        "frontend": "next",
                        "backend": "node",
                    }
                ),
                encoding="utf-8",
            )
            cli = SuperDevCLI()
            result = cli.run(["spec", "init"])
            assert result == 0
            assert (temp_project_dir / ".super-dev" / "WORKFLOW.md").exists()
            assert (temp_project_dir / "output" / "demo-bootstrap.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_help_and_version_alias_do_not_trigger_pipeline(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            assert cli.run(["help"]) == 0
            assert cli.run(["version"]) == 0
            assert not (temp_project_dir / "output").exists()
        finally:
            os.chdir(original_cwd)

    def test_pipeline_requires_ready_host_without_override(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")
        monkeypatch.delenv("SUPER_DEV_ALLOW_NO_HOST", raising=False)

        try:
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_direct_requirement_entry_generates_core_artifacts(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["构建一个支持登录和看板的平台"])
            assert result == 0

            output_dir = temp_project_dir / "output"
            assert any(output_dir.glob("*-research.md"))
            assert any(output_dir.glob("*-prd.md"))
            assert any(output_dir.glob("*-architecture.md"))
            assert any(output_dir.glob("*-uiux.md"))
            assert any(output_dir.glob("*-quality-gate.md"))
            assert any(output_dir.glob("*-pipeline-metrics.json"))
            assert any(output_dir.glob("*-pipeline-metrics.md"))
            assert any(output_dir.glob("*-frontend-runtime.md"))
            assert any(output_dir.glob("*-frontend-runtime.json"))
            assert (temp_project_dir / "preview.html").exists()
            assert any((output_dir / "rehearsal").glob("*-launch-rehearsal.md"))
            assert any((output_dir / "rehearsal").glob("*-rollback-playbook.md"))
            assert any((output_dir / "rehearsal").glob("*-smoke-checklist.md"))
            assert any((output_dir / "rehearsal").glob("*-rehearsal-report.md"))
            assert any((output_dir / "rehearsal").glob("*-rehearsal-report.json"))
            assert any((temp_project_dir / "output" / "delivery").glob("*-delivery-manifest.json"))
        finally:
            os.chdir(original_cwd)

    def test_direct_requirement_supports_pipeline_flags(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(
                [
                    "构建一个支持登录和看板的平台",
                    "--offline",
                    "--domain",
                    "saas",
                    "--backend",
                    "python",
                    "--name",
                    "direct-flags-demo",
                ]
            )
            assert result == 0

            output_dir = temp_project_dir / "output"
            assert (output_dir / "direct-flags-demo-prd.md").exists()
            assert (output_dir / "direct-flags-demo-architecture.md").exists()
            assert (output_dir / "direct-flags-demo-quality-gate.md").exists()
            assert (output_dir / "direct-flags-demo-frontend-runtime.json").exists()

            config_data = yaml.safe_load((temp_project_dir / "super-dev.yaml").read_text(encoding="utf-8"))
            assert config_data["domain"] == "saas"
            assert config_data["backend"] == "python"
        finally:
            os.chdir(original_cwd)

    def test_wizard_runs_pipeline_with_idea(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(
                [
                    "wizard",
                    "--idea",
                    "构建一个支持登录和看板的平台",
                    "--quick",
                    "--name",
                    "wizard-demo",
                    "--domain",
                    "saas",
                    "--offline",
                ]
            )
            assert result == 0

            output_dir = temp_project_dir / "output"
            assert (output_dir / "wizard-demo-prd.md").exists()
            assert (output_dir / "wizard-demo-architecture.md").exists()
            assert (output_dir / "wizard-demo-quality-gate.md").exists()
            assert (output_dir / "wizard-demo-frontend-runtime.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_wizard_quick_requires_idea(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["wizard", "--quick"])
            assert result == 2
        finally:
            os.chdir(original_cwd)

    def test_pipeline_generates_core_artifacts(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台"])
            assert result == 0

            output_dir = temp_project_dir / "output"
            assert any(output_dir.glob("*-research.md"))
            assert any(output_dir.glob("*-prd.md"))
            assert any(output_dir.glob("*-architecture.md"))
            assert any(output_dir.glob("*-uiux.md"))
            assert any(output_dir.glob("*-execution-plan.md"))
            assert any(output_dir.glob("*-frontend-blueprint.md"))
            assert any(output_dir.glob("*-frontend-runtime.md"))
            assert any(output_dir.glob("*-frontend-runtime.json"))
            assert any(output_dir.glob("*-ai-prompt.md"))
            assert any(output_dir.glob("*-task-execution.md"))
            assert any(output_dir.glob("*-pipeline-metrics.json"))
            assert any(output_dir.glob("*-pipeline-metrics.md"))
            assert (temp_project_dir / "preview.html").exists()

            assert (temp_project_dir / "frontend" / "src" / "App.tsx").exists()
            assert (temp_project_dir / "backend" / "API_CONTRACT.md").exists()
            assert (temp_project_dir / "backend" / "src" / "routes" / "auth.route.js").exists()
            assert (temp_project_dir / "backend" / "src" / "services" / "auth.service.js").exists()
            assert any((temp_project_dir / "backend" / "migrations").glob("*_create_auth.sql"))
            assert (temp_project_dir / ".github" / "workflows" / "ci.yml").exists()
            assert (temp_project_dir / ".gitlab-ci.yml").exists()
            assert (temp_project_dir / "Jenkinsfile").exists()
            assert (temp_project_dir / ".azure-pipelines.yml").exists()
            assert (temp_project_dir / "bitbucket-pipelines.yml").exists()
            assert (temp_project_dir / ".env.deploy.example").exists()
            assert (temp_project_dir / "output" / "deploy" / "all-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / "github-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / "gitlab-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / "jenkins-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / "azure-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / "bitbucket-secrets-checklist.md").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / ".env.deploy.github.example").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / ".env.deploy.gitlab.example").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / ".env.deploy.jenkins.example").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / ".env.deploy.azure.example").exists()
            assert (temp_project_dir / "output" / "deploy" / "platforms" / ".env.deploy.bitbucket.example").exists()
            assert any((temp_project_dir / "output" / "delivery").glob("*-delivery-manifest.json"))
            assert any((temp_project_dir / "output" / "delivery").glob("*-delivery-report.md"))
            assert any((temp_project_dir / "output" / "delivery").glob("*-delivery-v*.zip"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-launch-rehearsal.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rollback-playbook.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-smoke-checklist.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rehearsal-report.md"))
            assert any((temp_project_dir / "output" / "rehearsal").glob("*-rehearsal-report.json"))
        finally:
            os.chdir(original_cwd)

    def test_fix_command_runs_explicit_bugfix_mode(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["fix", "优化登录体验并补充回归验证"])
            assert result == 0

            output_dir = temp_project_dir / "output"
            plan_files = list(output_dir.glob("*-execution-plan.md"))
            assert plan_files
            plan = max(plan_files, key=lambda item: item.stat().st_mtime).read_text(encoding="utf-8")
            assert "> **请求模式**: bugfix" in plan
            assert "问题复现与影响分析" in plan
        finally:
            os.chdir(original_cwd)

    def test_pipeline_skip_rehearsal_verify(self, temp_project_dir: Path, monkeypatch, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            policy_dir = temp_project_dir / ".super-dev"
            policy_dir.mkdir(parents=True, exist_ok=True)
            (policy_dir / "policy.yaml").write_text(
                yaml.safe_dump(
                    {
                        "require_redteam": True,
                        "require_quality_gate": True,
                        "require_rehearsal_verify": False,
                        "min_quality_threshold": 80,
                        "allowed_cicd_platforms": ["all"],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            cli = SuperDevCLI()
            result = cli.run(
                ["pipeline", "构建一个支持登录和看板的平台", "--skip-rehearsal-verify"]
            )
            assert result == 0
            output = capsys.readouterr().out
            assert "流程完成（存在跳过门禁）" in output
            assert "这不等于严格意义上的“全部通过”" in output
            assert "已跳过门禁: 发布演练验证" in output
            assert any((temp_project_dir / "output").glob("*-frontend-runtime.json"))
            rehearsal_dir = temp_project_dir / "output" / "rehearsal"
            assert any(rehearsal_dir.glob("*-launch-rehearsal.md"))
            assert any(rehearsal_dir.glob("*-rollback-playbook.md"))
            assert any(rehearsal_dir.glob("*-smoke-checklist.md"))
            assert not any(rehearsal_dir.glob("*-rehearsal-report.md"))
            assert not any(rehearsal_dir.glob("*-rehearsal-report.json"))
        finally:
            os.chdir(original_cwd)

    def test_pipeline_supports_saas_domain(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台", "--domain", "saas"])
            assert result == 0
            assert any((temp_project_dir / "output").glob("*-prd.md"))
            assert any((temp_project_dir / "output").glob("*-frontend-runtime.json"))
        finally:
            os.chdir(original_cwd)

    def test_pipeline_fails_when_delivery_package_is_incomplete(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()

            from super_dev.deployers.delivery import DeliveryPackager

            original_package = DeliveryPackager.package

            def fake_package(self, cicd_platform="all"):
                payload = original_package(self, cicd_platform=cicd_platform)
                return {
                    **payload,
                    "status": "incomplete",
                    "missing_required_count": 1,
                    "missing_required": [{"path": "output/demo-frontend-runtime.json", "reason": "missing"}],
                }

            monkeypatch.setattr(DeliveryPackager, "package", fake_package)

            result = cli.run(["pipeline", "构建一个支持登录和看板的平台"])
            assert result == 1

            run_state_file = temp_project_dir / ".super-dev" / "runs" / "last-pipeline.json"
            payload = json.loads(run_state_file.read_text(encoding="utf-8"))
            assert payload["failure_reason"] == "delivery_packaging_incomplete"
            assert payload["failed_stage"] == "11"
            assert payload["status_normalized"] == "failed"
        finally:
            os.chdir(original_cwd)

    def test_pipeline_pauses_at_docs_confirmation_gate(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台"])
            assert result == 0

            output_dir = temp_project_dir / "output"
            assert any(output_dir.glob("*-research.md"))
            assert any(output_dir.glob("*-prd.md"))
            assert any(output_dir.glob("*-architecture.md"))
            assert any(output_dir.glob("*-uiux.md"))
            assert not any((temp_project_dir / ".super-dev" / "changes").glob("*/tasks.md"))

            run_state_file = temp_project_dir / ".super-dev" / "runs" / "last-pipeline.json"
            payload = json.loads(run_state_file.read_text(encoding="utf-8"))
            assert payload["status"] == "waiting_confirmation"
            assert payload["resume_from_stage"] == "2"
            assert payload["status_normalized"] == "running"
        finally:
            os.chdir(original_cwd)


class TestCLIRunControl:
    """测试 run 控制命令（恢复）"""

    def test_write_pipeline_run_state_creates_lock_file(self, temp_project_dir: Path):
        cli = SuperDevCLI()
        cli._write_pipeline_run_state(
            temp_project_dir,
            {"status": "running", "project_name": "demo"},
        )
        lock_file = temp_project_dir / ".super-dev" / "runs" / ".runs.lock"
        assert lock_file.exists()
        state_file = temp_project_dir / ".super-dev" / "runs" / "last-pipeline.json"
        payload = json.loads(state_file.read_text(encoding="utf-8"))
        assert payload["status_normalized"] == "running"

    def test_run_resume_returns_error_for_corrupted_state_file(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            run_state_dir = temp_project_dir / ".super-dev" / "runs"
            run_state_dir.mkdir(parents=True, exist_ok=True)
            (run_state_dir / "last-pipeline.json").write_text("{invalid-json", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["run", "--resume"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_run_resume_replays_failed_pipeline(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            run_state_dir = temp_project_dir / ".super-dev" / "runs"
            run_state_dir.mkdir(parents=True, exist_ok=True)
            (run_state_dir / "last-pipeline.json").write_text(
                json.dumps(
                    {
                        "status": "failed",
                        "project_name": "resume-demo",
                        "pipeline_args": {
                            "description": "构建一个支持登录和看板的平台",
                            "platform": "web",
                            "frontend": "react",
                            "backend": "python",
                            "domain": "saas",
                            "name": "resume-demo",
                            "cicd": "all",
                            "skip_redteam": False,
                            "skip_scaffold": False,
                            "skip_quality_gate": False,
                            "skip_rehearsal_verify": False,
                            "offline": True,
                            "quality_threshold": None,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            captured: dict[str, object] = {}

            def _fake_pipeline(pipeline_args):
                captured["args"] = pipeline_args
                return 0

            monkeypatch.setattr(cli, "_cmd_pipeline", _fake_pipeline)
            result = cli.run(["run", "--resume"])
            assert result == 0
            assert "args" in captured
            pipeline_args = captured["args"]
            assert getattr(pipeline_args, "resume") is True
            assert getattr(pipeline_args, "name") == "resume-demo"
            assert getattr(pipeline_args, "description") == "构建一个支持登录和看板的平台"
        finally:
            os.chdir(original_cwd)

    def test_run_resume_supports_interrupted_running_state(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            run_state_dir = temp_project_dir / ".super-dev" / "runs"
            run_state_dir.mkdir(parents=True, exist_ok=True)
            (run_state_dir / "last-pipeline.json").write_text(
                json.dumps(
                    {
                        "status": "running",
                        "project_name": "resume-demo",
                        "pipeline_args": {
                            "description": "构建一个支持登录和看板的平台",
                            "platform": "web",
                            "frontend": "react",
                            "backend": "python",
                            "domain": "saas",
                            "name": "resume-demo",
                            "cicd": "all",
                            "skip_redteam": False,
                            "skip_scaffold": False,
                            "skip_quality_gate": False,
                            "skip_rehearsal_verify": False,
                            "offline": True,
                            "quality_threshold": None,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            captured: dict[str, object] = {}

            def _fake_pipeline(pipeline_args):
                captured["args"] = pipeline_args
                return 0

            monkeypatch.setattr(cli, "_cmd_pipeline", _fake_pipeline)
            result = cli.run(["run", "--resume"])
            assert result == 0
            assert "args" in captured
            pipeline_args = captured["args"]
            assert getattr(pipeline_args, "resume") is True
            assert getattr(pipeline_args, "name") == "resume-demo"
        finally:
            os.chdir(original_cwd)

    def test_run_resume_supports_waiting_confirmation_state(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            run_state_dir = temp_project_dir / ".super-dev" / "runs"
            run_state_dir.mkdir(parents=True, exist_ok=True)
            (run_state_dir / "last-pipeline.json").write_text(
                json.dumps(
                    {
                        "status": "waiting_confirmation",
                        "project_name": "resume-demo",
                        "resume_from_stage": "2",
                        "pipeline_args": {
                            "description": "构建一个支持登录和看板的平台",
                            "platform": "web",
                            "frontend": "react",
                            "backend": "python",
                            "domain": "saas",
                            "name": "resume-demo",
                            "cicd": "all",
                            "skip_redteam": False,
                            "skip_scaffold": False,
                            "skip_quality_gate": False,
                            "skip_rehearsal_verify": False,
                            "offline": True,
                            "quality_threshold": None,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            save_docs_confirmation(
                temp_project_dir,
                {
                    "status": "confirmed",
                    "comment": "三文档已确认",
                    "actor": "pytest",
                    "run_id": "resume-demo",
                },
            )

            cli = SuperDevCLI()
            captured: dict[str, object] = {}

            def _fake_pipeline(pipeline_args):
                captured["args"] = pipeline_args
                return 0

            monkeypatch.setattr(cli, "_cmd_pipeline", _fake_pipeline)
            result = cli.run(["run", "--resume"])
            assert result == 0
            pipeline_args = captured["args"]
            assert getattr(pipeline_args, "resume") is True
            assert getattr(pipeline_args, "name") == "resume-demo"
        finally:
            os.chdir(original_cwd)

    def test_run_resume_blocks_when_ui_revision_requested(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            run_state_dir = temp_project_dir / ".super-dev" / "runs"
            run_state_dir.mkdir(parents=True, exist_ok=True)
            (run_state_dir / "last-pipeline.json").write_text(
                json.dumps(
                    {
                        "status": "waiting_ui_revision",
                        "project_name": "resume-demo",
                        "resume_from_stage": "2",
                        "pipeline_args": {
                            "description": "重做官网",
                            "platform": "web",
                            "frontend": "react",
                            "backend": "python",
                            "domain": "saas",
                            "name": "resume-demo",
                            "cicd": "all",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            save_ui_revision(
                temp_project_dir,
                {
                    "status": "revision_requested",
                    "comment": "Hero 太空，重做首屏",
                    "actor": "pytest",
                    "run_id": "resume-demo",
                },
            )

            cli = SuperDevCLI()
            result = cli.run(["run", "--resume"])

            assert result == 1
            output = capsys.readouterr().out
            assert "UI 改版门" in output
            assert "super-dev review ui --status confirmed" in output
        finally:
            os.chdir(original_cwd)

    def test_spec_propose_blocks_when_ui_revision_requested(self, temp_project_dir: Path, capsys):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            for suffix in ("prd", "architecture", "uiux"):
                (output_dir / f"demo-{suffix}.md").write_text("# ok", encoding="utf-8")
            save_docs_confirmation(
                temp_project_dir,
                {
                    "status": "confirmed",
                    "comment": "三文档已确认",
                    "actor": "pytest",
                    "run_id": "spec-demo",
                },
            )
            save_ui_revision(
                temp_project_dir,
                {
                    "status": "revision_requested",
                    "comment": "需要重做 UI",
                    "actor": "pytest",
                    "run_id": "spec-demo",
                },
            )

            cli = SuperDevCLI()
            result = cli.run(
                [
                    "spec",
                    "propose",
                    "demo-change",
                    "--title",
                    "demo",
                    "--description",
                    "demo desc",
                ]
            )

            assert result == 1
            output = capsys.readouterr().out
            assert "必须先完成 UI 改版返工" in output
            assert "super-dev review ui --status confirmed" in output
        finally:
            os.chdir(original_cwd)

    def test_run_resume_requires_state(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["run", "--resume"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_pipeline_knowledge_cache_contains_signature(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            _confirm_docs(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台"])
            assert result == 0

            cache_files = list((temp_project_dir / "output" / "knowledge-cache").glob("*-knowledge-bundle.json"))
            assert cache_files
            content = cache_files[0].read_text(encoding="utf-8")
            assert '"cache_signature"' in content
            assert '"cache_ttl_seconds"' in content
        finally:
            os.chdir(original_cwd)

    def test_pipeline_knowledge_settings_from_project_config(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            (temp_project_dir / "super-dev.yaml").write_text(
                (
                    "name: demo\n"
                    "platform: web\n"
                    "frontend: react\n"
                    "backend: node\n"
                    "knowledge_allowed_domains:\n"
                    "  - openai.com\n"
                    "  - python.org\n"
                    "knowledge_cache_ttl_seconds: 120\n"
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台", "--name", "demo"])
            assert result == 0

            cache_file = temp_project_dir / "output" / "knowledge-cache" / "demo-knowledge-bundle.json"
            assert cache_file.exists()
            cache_payload = json.loads(cache_file.read_text(encoding="utf-8"))
            assert cache_payload.get("cache_ttl_seconds") == 120
            metadata = cache_payload.get("metadata", {})
            assert metadata.get("allowed_web_domains") == ["openai.com", "python.org"]

            metrics_file = temp_project_dir / "output" / "demo-pipeline-metrics.json"
            assert metrics_file.exists()
            metrics_payload = json.loads(metrics_file.read_text(encoding="utf-8"))
            stages = metrics_payload.get("stages", [])
            stage0 = next((item for item in stages if item.get("stage") == "0"), {})
            details = stage0.get("details", {})
            assert details.get("knowledge_cache_ttl_seconds") == 120
            assert details.get("knowledge_allowed_domains") == ["openai.com", "python.org"]
        finally:
            os.chdir(original_cwd)

    def test_metrics_command_reads_latest_pipeline_metrics(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            metrics_file = output_dir / "demo-pipeline-metrics.json"
            metrics_file.write_text(
                (
                    "{\n"
                    '  "project_name": "demo",\n'
                    '  "success": true,\n'
                    '  "success_rate": 100,\n'
                    '  "total_duration_seconds": 12.3,\n'
                    '  "stages": []\n'
                    "}\n"
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["metrics"])
            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_metrics_history_command_reads_history_files(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            history_dir = temp_project_dir / "output" / "metrics-history"
            history_dir.mkdir(parents=True, exist_ok=True)
            (history_dir / "demo-pipeline-metrics-20260303T010000Z.json").write_text(
                (
                    "{\n"
                    '  "project_name": "demo",\n'
                    '  "success": true,\n'
                    '  "success_rate": 100,\n'
                    '  "total_duration_seconds": 12.3,\n'
                    '  "started_at": "2026-03-03T01:00:00Z",\n'
                    '  "stages": []\n'
                    "}\n"
                ),
                encoding="utf-8",
            )
            (history_dir / "demo-pipeline-metrics-20260303T020000Z.json").write_text(
                (
                    "{\n"
                    '  "project_name": "demo",\n'
                    '  "success": false,\n'
                    '  "success_rate": 80,\n'
                    '  "total_duration_seconds": 16.8,\n'
                    '  "started_at": "2026-03-03T02:00:00Z",\n'
                    '  "stages": []\n'
                    "}\n"
                ),
                encoding="utf-8",
            )

            cli = SuperDevCLI()
            result = cli.run(["metrics", "--history", "--limit", "2"])
            assert result == 0
        finally:
            os.chdir(original_cwd)

    def test_metrics_command_invalid_json_returns_error(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            output_dir = temp_project_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "demo-pipeline-metrics.json").write_text("{invalid-json", encoding="utf-8")

            cli = SuperDevCLI()
            result = cli.run(["metrics"])
            assert result == 1
        finally:
            os.chdir(original_cwd)

    def test_release_readiness_command_is_not_routed_as_direct_requirement(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            _prepare_release_ready_project(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["release", "readiness"])

            assert result == 0
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-release-readiness.md").exists()
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-release-readiness.json").exists()
        finally:
            os.chdir(original_cwd)

    def test_release_readiness_command_json_output(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            _prepare_release_ready_project(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["release", "readiness", "--json"])

            assert result == 0
            payload = json.loads(
                (temp_project_dir / "output" / f"{temp_project_dir.name}-release-readiness.json").read_text(
                    encoding="utf-8"
                )
            )
            assert payload["passed"] is True
            assert payload["score"] == 100
            assert any(check["name"] == "Spec Quality" for check in payload["checks"])
        finally:
            os.chdir(original_cwd)

    def test_release_proof_pack_command_json_output(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            _prepare_proof_pack_project(temp_project_dir)
            cli = SuperDevCLI()
            result = cli.run(["release", "proof-pack", "--json"])

            assert result == 0
            payload = json.loads(
                (temp_project_dir / "output" / f"{temp_project_dir.name}-proof-pack.json").read_text(
                    encoding="utf-8"
                )
            )
            assert payload["status"] == "ready"
            assert payload["ready_count"] == payload["total_count"]
            assert payload["summary"]["blocking_count"] == 0
            assert any(artifact["name"] == "Spec Quality" for artifact in payload["artifacts"])
            assert any(artifact["name"] == "Scope Coverage" for artifact in payload["artifacts"])
            assert any(artifact["name"] == "Repo Map" for artifact in payload["artifacts"])
            assert any(artifact["name"] == "Dependency Graph" for artifact in payload["artifacts"])
            assert any(artifact["name"] == "Impact Analysis" for artifact in payload["artifacts"])
            assert any(artifact["name"] == "Regression Guard" for artifact in payload["artifacts"])
            assert (temp_project_dir / "output" / f"{temp_project_dir.name}-proof-pack-summary.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_release_proof_pack_marks_rehearsal_artifact_ready_when_report_exists(
        self, temp_project_dir: Path
    ):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            _prepare_proof_pack_project(temp_project_dir)
            (temp_project_dir / "output" / "rehearsal" / f"{temp_project_dir.name}-rehearsal-report.json").write_text(
                json.dumps({"passed": False, "score": 35}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            cli = SuperDevCLI()
            result = cli.run(["release", "proof-pack", "--json"])

            # rehearsal passed=False -> proof-pack 有 blocker，命令可能返回 1
            assert result in (0, 1)
            payload = json.loads(
                (temp_project_dir / "output" / f"{temp_project_dir.name}-proof-pack.json").read_text(
                    encoding="utf-8"
                )
            )
            rehearsal = next(item for item in payload["artifacts"] if item["name"] == "Release Rehearsal")
            assert rehearsal["status"] == "pending"  # passed=False -> pending
            assert "passed=False" in rehearsal["summary"]
        finally:
            os.chdir(original_cwd)


class TestCLIClean:
    def test_clean_empty_output(self, temp_project_dir):
        original = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["clean"])
            assert result == 0
        finally:
            os.chdir(original)

    def test_clean_dry_run(self, temp_project_dir):
        original = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            out = temp_project_dir / "output"
            out.mkdir()
            (out / "test-prd.md").write_text("x")
            (out / "test-architecture.md").write_text("x")
            cli = SuperDevCLI()
            result = cli.run(["clean", "--dry-run"])
            assert result == 0
            assert (out / "test-prd.md").exists()
            assert (out / "test-architecture.md").exists()
        finally:
            os.chdir(original)

    def test_clean_all(self, temp_project_dir):
        original = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            out = temp_project_dir / "output"
            out.mkdir()
            (out / "test-prd.md").write_text("x")
            (out / "test-architecture.md").write_text("x")
            cli = SuperDevCLI()
            result = cli.run(["clean", "--all"])
            assert result == 0
            remaining = list(out.glob("*"))
            assert len(remaining) == 0
        finally:
            os.chdir(original)

    def test_clean_keep_default(self, temp_project_dir):
        original = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            out = temp_project_dir / "output"
            out.mkdir()
            (out / "test-prd.md").write_text("x")
            (out / "test-architecture.md").write_text("x")
            import time
            time.sleep(0.05)
            (out / "test-uiux.md").write_text("y")
            cli = SuperDevCLI()
            result = cli.run(["clean"])
            assert result == 0
        finally:
            os.chdir(original)
