"""
Super Dev CLI 集成测试
"""

import os
from pathlib import Path

import pytest
import yaml

from super_dev.cli import SuperDevCLI


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

    def test_integrate_setup_cursor(self, temp_project_dir: Path):
        original_cwd = os.getcwd()
        os.chdir(temp_project_dir)
        try:
            cli = SuperDevCLI()
            result = cli.run(["integrate", "setup", "--target", "cursor", "--force"])
            assert result == 0
            assert (temp_project_dir / ".cursorrules").exists()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.parametrize(
        "target, expected_file",
        [
            ("claude-code", ".claude/CLAUDE.md"),
            ("codex-cli", ".codex/AGENTS.md"),
            ("opencode", ".opencode/AGENTS.md"),
            ("cursor", ".cursorrules"),
            ("qoder", ".qoder/rules.md"),
            ("trae", ".trae/rules.md"),
            ("codebuddy", ".codebuddy/rules.md"),
            ("antigravity", ".agents/workflows/super-dev.md"),
        ],
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
        [
            "claude-code",
            "codex-cli",
            "opencode",
            "cursor",
            "qoder",
            "trae",
            "codebuddy",
            "antigravity",
        ],
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


class TestCLIPipeline:
    """测试完整流水线关键产物"""

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

            assert (temp_project_dir / "frontend" / "src" / "App.tsx").exists()
            assert (temp_project_dir / "backend" / "API_CONTRACT.md").exists()
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
        finally:
            os.chdir(original_cwd)
