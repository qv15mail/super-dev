"""
CI/CD 生成器测试
"""

from pathlib import Path

from super_dev.deployers import CICDGenerator


class TestCICDGenerator:
    def test_generate_all_platforms(self, temp_project_dir: Path):
        generator = CICDGenerator(
            project_dir=temp_project_dir,
            name="demo-app",
            tech_stack={"frontend": "react", "backend": "node"},
            platform="all",
        )

        files = generator.generate()
        assert ".github/workflows/ci.yml" in files
        assert ".github/workflows/cd.yml" in files
        assert ".gitlab-ci.yml" in files
        assert "Jenkinsfile" in files
        assert ".azure-pipelines.yml" in files
        assert "bitbucket-pipelines.yml" in files

    def test_github_template_expressions_are_valid(self, temp_project_dir: Path):
        generator = CICDGenerator(
            project_dir=temp_project_dir,
            name="demo-app",
            tech_stack={"frontend": "react", "backend": "node"},
            platform="github",
        )
        files = generator.generate()
        ci = files[".github/workflows/ci.yml"]
        cd = files[".github/workflows/cd.yml"]

        assert "if: ${{ hashFiles('frontend/package.json') != '' }}" in ci
        assert "npm --prefix frontend ci" in ci
        assert "npm --prefix backend run lint --if-present" in ci
        assert "${{ secrets.DOCKER_USERNAME }}" in ci
        assert "${{ github.sha }}" in ci
        assert "{{ '{{' }}" not in ci

        assert "branches: [main, develop]" in cd
        assert "${{ secrets.KUBE_CONFIG_PROD }}" in cd
        assert "backup-${{ github.sha }}.yaml" in cd
        assert "for i in {1..30}; do" in cd

    def test_bitbucket_template_has_correct_variables(self, temp_project_dir: Path):
        generator = CICDGenerator(
            project_dir=temp_project_dir,
            name="demo-app",
            tech_stack={"frontend": "react", "backend": "node"},
            platform="bitbucket",
        )
        files = generator.generate()
        content = files["bitbucket-pipelines.yml"]

        assert "${REGISTRY_URL}/demo-app:${BITBUCKET_BUILD_NUMBER}" in content
        assert "npm --prefix frontend run lint --if-present" in content
        assert "KUBE_CONFIG: ${KUBE_CONFIG_PROD}" in content
        assert "KUBE_CONFIG: ${KUBE_CONFIG_DEV}" in content

    def test_sanitize_non_ascii_project_name_for_infra(self, temp_project_dir: Path):
        generator = CICDGenerator(
            project_dir=temp_project_dir,
            name="用户认证系统",
            tech_stack={"frontend": "react", "backend": "node"},
            platform="github",
        )
        files = generator.generate()
        ci = files[".github/workflows/ci.yml"]
        cd = files[".github/workflows/cd.yml"]

        assert "/super-dev-app:latest" in ci
        assert "deployment/super-dev-app" in cd
