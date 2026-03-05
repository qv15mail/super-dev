"""
Super Dev CLI 集成测试
"""

import json
import os
from pathlib import Path

import pytest
import yaml

from super_dev.cli import SuperDevCLI
from super_dev.integrations import IntegrationManager
from super_dev.skills import SkillManager


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
            assert isinstance(payload, list)
            assert len(payload) == 1
            row = payload[0]
            assert row["host"] == "qoder"
            assert row["adapter_mode"] == "native-ide-rule-file"
            assert "official_docs_url" in row
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
    def test_skill_builtin_install_each_target(self, temp_project_dir: Path, target: str):
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

    def test_onboard_single_host_installs_all_components(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--host", "claude-code", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".claude" / "CLAUDE.md").exists()
            assert (temp_project_dir / ".claude" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert (temp_project_dir / ".claude" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_yes_defaults_to_all_targets(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["onboard", "--yes", "--force", "--skip-skill"])
            assert result == 0
            assert (temp_project_dir / ".claude" / "CLAUDE.md").exists()
            assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
            assert (temp_project_dir / ".kimi" / "AGENTS.md").exists()
            assert (temp_project_dir / ".qoder" / "rules.md").exists()
            assert (temp_project_dir / ".claude" / "commands" / "super-dev.md").exists()
            assert (temp_project_dir / ".kimi" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_onboard_auto_detects_targets_from_path(self, temp_project_dir: Path):
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
            assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
            assert (temp_project_dir / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
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

    def test_doctor_repair_fixes_host_issues(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            before = cli.run(["doctor", "--host", "codex-cli"])
            assert before == 1

            repaired = cli.run(["doctor", "--host", "codex-cli", "--repair", "--force"])
            assert repaired == 0

            assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
            assert (temp_project_dir / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
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
            assert "require_redteam" in output
            assert "min_quality_threshold" in output
            assert "enforce_required_hosts_ready" in output
        finally:
            os.chdir(original_cwd)

    def test_setup_host_runs_onboard_and_doctor(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["setup", "--host", "codex-cli", "--force"])
            assert result == 0
            assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
            assert (temp_project_dir / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
        finally:
            os.chdir(original_cwd)

    def test_install_host_runs_setup_flow(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["install", "--host", "codex-cli", "--force", "--yes"])
            assert result == 0
            assert (temp_project_dir / ".codex" / "AGENTS.md").exists()
            assert (temp_project_dir / ".codex" / "skills" / "super-dev-core" / "SKILL.md").exists()
            assert (temp_project_dir / ".codex" / "commands" / "super-dev.md").exists()
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
            assert any(output_dir.glob("*-ai-prompt.md"))
            assert any(output_dir.glob("*-task-execution.md"))
            assert any(output_dir.glob("*-pipeline-metrics.json"))
            assert any(output_dir.glob("*-pipeline-metrics.md"))

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

    def test_pipeline_skip_rehearsal_verify(self, temp_project_dir: Path, monkeypatch):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        monkeypatch.setenv("SUPER_DEV_DISABLE_WEB", "1")

        try:
            cli = SuperDevCLI()
            result = cli.run(
                ["pipeline", "构建一个支持登录和看板的平台", "--skip-rehearsal-verify"]
            )
            assert result == 0
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
            cli = SuperDevCLI()
            result = cli.run(["pipeline", "构建一个支持登录和看板的平台", "--domain", "saas"])
            assert result == 0
            assert any((temp_project_dir / "output").glob("*-prd.md"))
        finally:
            os.chdir(original_cwd)


class TestCLIRunControl:
    """测试 run 控制命令（恢复）"""

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
