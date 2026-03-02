"""
实现骨架生成器测试
"""

from pathlib import Path

from super_dev.creators.implementation_builder import ImplementationScaffoldBuilder


class TestImplementationScaffoldBuilder:
    def test_generate_react_node_scaffold(self, temp_project_dir: Path):
        builder = ImplementationScaffoldBuilder(
            project_dir=temp_project_dir,
            name="demo",
            frontend="react",
            backend="node",
        )
        result = builder.generate(
            requirements=[
                {"spec_name": "auth", "req_name": "secure-authentication"},
                {"spec_name": "dashboard", "req_name": "dashboard-insights"},
            ]
        )

        assert len(result["frontend_files"]) > 0
        assert len(result["backend_files"]) > 0
        assert (temp_project_dir / "frontend" / "src" / "App.tsx").exists()
        assert (temp_project_dir / "backend" / "src" / "app.js").exists()
        assert (temp_project_dir / "backend" / "src" / "app.test.js").exists()
        assert (temp_project_dir / "backend" / "src" / "routes" / "auth.route.js").exists()
        assert (temp_project_dir / "backend" / "src" / "services" / "auth.service.js").exists()
        assert (temp_project_dir / "backend" / "src" / "repositories" / "auth.repository.js").exists()
        assert (temp_project_dir / "backend" / "tests" / "auth.service.test.js").exists()
        assert (temp_project_dir / "backend" / "migrations" / "001_create_auth.sql").exists()
        assert (temp_project_dir / "backend" / "API_CONTRACT.md").exists()

    def test_generate_python_backend_scaffold(self, temp_project_dir: Path):
        builder = ImplementationScaffoldBuilder(
            project_dir=temp_project_dir,
            name="demo",
            frontend="none",
            backend="python",
        )
        result = builder.generate(requirements=[{"spec_name": "core", "req_name": "flow"}])

        assert result["frontend_files"] == []
        assert (temp_project_dir / "backend" / "src" / "app.py").exists()
        assert (temp_project_dir / "backend" / "src" / "routes" / "core_route.py").exists()
        assert (temp_project_dir / "backend" / "src" / "services" / "core_service.py").exists()
        assert (temp_project_dir / "backend" / "src" / "repositories" / "core_repository.py").exists()
        assert (temp_project_dir / "backend" / "requirements.txt").exists()
        assert (temp_project_dir / "backend" / "tests" / "test_smoke.py").exists()
        assert (temp_project_dir / "backend" / "tests" / "test_core_service.py").exists()
        assert (temp_project_dir / "backend" / "migrations" / "001_create_core.sql").exists()

    def test_generate_vue_go_scaffold(self, temp_project_dir: Path):
        builder = ImplementationScaffoldBuilder(
            project_dir=temp_project_dir,
            name="demo",
            frontend="vue",
            backend="go",
        )
        result = builder.generate(requirements=[{"spec_name": "dashboard", "req_name": "insights"}])

        assert len(result["frontend_files"]) > 0
        assert len(result["backend_files"]) > 0
        assert (temp_project_dir / "frontend" / "src" / "App.vue").exists()
        assert (temp_project_dir / "frontend" / "vite.config.js").exists()
        assert (temp_project_dir / "backend" / "src" / "main.go").exists()

    def test_package_names_are_sanitized(self, temp_project_dir: Path):
        builder = ImplementationScaffoldBuilder(
            project_dir=temp_project_dir,
            name="用户认证系统",
            frontend="react",
            backend="node",
        )
        builder.generate(requirements=[{"spec_name": "auth", "req_name": "secure-authentication"}])

        frontend_pkg = (temp_project_dir / "frontend" / "package.json").read_text(encoding="utf-8")
        backend_pkg = (temp_project_dir / "backend" / "package.json").read_text(encoding="utf-8")
        assert '"name": "super-dev-app-frontend"' in frontend_pkg
        assert '"name": "super-dev-app-backend"' in backend_pkg
