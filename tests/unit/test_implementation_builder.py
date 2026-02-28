# -*- coding: utf-8 -*-
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
        assert (temp_project_dir / "backend" / "requirements.txt").exists()

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
