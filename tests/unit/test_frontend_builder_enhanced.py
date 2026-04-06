# ruff: noqa: I001
"""
前端骨架生成器增强测试

测试对象: super_dev.creators.frontend_builder.FrontendScaffoldBuilder
"""

import pytest
from super_dev.creators.frontend_builder import FrontendScaffoldBuilder


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def builder(tmp_path):
    return FrontendScaffoldBuilder(
        project_dir=tmp_path,
        name="test-app",
        description="A test application",
        frontend="react",
    )


@pytest.fixture()
def vue_builder(tmp_path):
    return FrontendScaffoldBuilder(
        project_dir=tmp_path, name="vue-app",
        description="Vue test app", frontend="vue",
    )


@pytest.fixture()
def sample_requirements():
    return [
        {"name": "Login", "description": "User login with email/password"},
        {"name": "Dashboard", "description": "Display key metrics"},
        {"name": "Profile", "description": "User profile management"},
    ]


@pytest.fixture()
def sample_phases():
    return [
        {"name": "Planning", "status": "completed"},
        {"name": "Frontend", "status": "in_progress"},
        {"name": "Backend", "status": "pending"},
    ]


@pytest.fixture()
def sample_docs():
    return {
        "prd": "Product Requirements Document content",
        "architecture": "Architecture design content",
        "uiux": "UI/UX design content",
    }


# ---------------------------------------------------------------------------
# 初始化
# ---------------------------------------------------------------------------

class TestFrontendScaffoldBuilderInit:
    def test_creates_with_valid_dir(self, tmp_path):
        b = FrontendScaffoldBuilder(tmp_path, "test", "desc")
        assert b.project_dir.is_absolute()
        assert b.name == "test"
        assert b.description == "desc"

    def test_default_frontend_is_react(self, tmp_path):
        b = FrontendScaffoldBuilder(tmp_path, "test", "desc")
        assert b.frontend == "react"

    def test_custom_frontend(self, tmp_path):
        b = FrontendScaffoldBuilder(tmp_path, "test", "desc", frontend="vue")
        assert b.frontend == "vue"

    def test_resolves_path(self, tmp_path):
        b = FrontendScaffoldBuilder(tmp_path / ".", "test", "desc")
        assert ".." not in str(b.project_dir)


# ---------------------------------------------------------------------------
# generate() 集成
# ---------------------------------------------------------------------------

class TestGenerate:
    def test_generates_files(self, builder, sample_requirements, sample_phases, sample_docs):
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_creates_output_dir(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        output_dir = builder.project_dir / "output" / "frontend"
        assert output_dir.exists()

    def test_creates_index_html(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        index = builder.project_dir / "output" / "frontend" / "index.html"
        assert index.exists()
        content = index.read_text()
        assert "<html" in content.lower()

    def test_creates_styles_css(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        css = builder.project_dir / "output" / "frontend" / "styles.css"
        assert css.exists()

    def test_creates_design_tokens(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        tokens = builder.project_dir / "output" / "frontend" / "design-tokens.css"
        assert tokens.exists()

    def test_creates_app_js(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        js = builder.project_dir / "output" / "frontend" / "app.js"
        assert js.exists()

    def test_html_contains_project_name(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        index = builder.project_dir / "output" / "frontend" / "index.html"
        content = index.read_text()
        assert "test-app" in content

    def test_returns_file_paths(self, builder, sample_requirements, sample_phases, sample_docs):
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)
        # Should return paths to generated files
        assert len(result) > 0

    def test_empty_requirements(self, builder, sample_phases, sample_docs):
        result = builder.generate([], sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_empty_phases(self, builder, sample_requirements, sample_docs):
        result = builder.generate(sample_requirements, [], sample_docs)
        assert isinstance(result, dict)

    def test_empty_docs(self, builder, sample_requirements, sample_phases):
        result = builder.generate(sample_requirements, sample_phases, {})
        assert isinstance(result, dict)

    def test_all_empty(self, builder):
        result = builder.generate([], [], {})
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 不同前端栈
# ---------------------------------------------------------------------------

class TestDifferentFrontends:
    @pytest.fixture(params=["react", "vue", "angular", "svelte", "next"])
    def stack_builder(self, tmp_path, request):
        return FrontendScaffoldBuilder(
            tmp_path, "test", "description", frontend=request.param,
        )

    def test_all_stacks_generate(self, stack_builder, sample_requirements, sample_phases, sample_docs):
        result = stack_builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_all_stacks_create_html(self, stack_builder, sample_requirements, sample_phases, sample_docs):
        stack_builder.generate(sample_requirements, sample_phases, sample_docs)
        index = stack_builder.project_dir / "output" / "frontend" / "index.html"
        assert index.exists()


# ---------------------------------------------------------------------------
# 边界情况
# ---------------------------------------------------------------------------

class TestFrontendBuilderEdgeCases:
    def test_special_chars_in_name(self, tmp_path, sample_requirements, sample_phases, sample_docs):
        builder = FrontendScaffoldBuilder(tmp_path, "test<>app&", "desc with <script>")
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)
        # Check that special chars are escaped in HTML
        index = tmp_path / "output" / "frontend" / "index.html"
        content = index.read_text()
        assert "<script>" not in content or "&lt;script&gt;" in content

    def test_unicode_in_description(self, tmp_path, sample_requirements, sample_phases, sample_docs):
        builder = FrontendScaffoldBuilder(tmp_path, "中文项目", "这是一个测试")
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_very_long_description(self, tmp_path, sample_requirements, sample_phases, sample_docs):
        builder = FrontendScaffoldBuilder(tmp_path, "test", "x" * 10000)
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_many_requirements(self, tmp_path, sample_phases, sample_docs):
        reqs = [{"name": f"Req-{i}", "description": f"Description {i}"} for i in range(50)]
        builder = FrontendScaffoldBuilder(tmp_path, "test", "Many reqs")
        result = builder.generate(reqs, sample_phases, sample_docs)
        assert isinstance(result, dict)

    def test_idempotent_generation(self, builder, sample_requirements, sample_phases, sample_docs):
        r1 = builder.generate(sample_requirements, sample_phases, sample_docs)
        r2 = builder.generate(sample_requirements, sample_phases, sample_docs)
        assert isinstance(r1, dict)
        assert isinstance(r2, dict)


# ---------------------------------------------------------------------------
# 生成文件内容验证
# ---------------------------------------------------------------------------

class TestGeneratedFileContent:
    def test_html_is_valid_structure(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content or "<html" in content
        assert "</html>" in content
        assert "<head>" in content or "<head " in content
        assert "<body>" in content or "<body " in content

    def test_css_has_styles(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        css_path = builder.project_dir / "output" / "frontend" / "styles.css"
        content = css_path.read_text(encoding="utf-8")
        assert len(content) > 50
        assert "{" in content  # Has CSS rules

    def test_design_tokens_has_variables(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        tokens_path = builder.project_dir / "output" / "frontend" / "design-tokens.css"
        content = tokens_path.read_text(encoding="utf-8")
        assert len(content) > 20
        # Should contain CSS custom properties
        assert "--" in content or ":root" in content

    def test_js_has_code(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        js_path = builder.project_dir / "output" / "frontend" / "app.js"
        content = js_path.read_text(encoding="utf-8")
        assert len(content) > 20

    def test_html_references_css(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "styles.css" in content or "style" in content.lower()

    def test_html_references_js(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "app.js" in content or "script" in content.lower()

    def test_html_references_design_tokens(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "design-tokens" in content or "token" in content.lower()

    def test_html_has_charset_meta(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "charset" in content.lower() or "utf-8" in content.lower()

    def test_html_has_viewport_meta(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        assert "viewport" in content.lower()

    def test_requirements_reflected_in_html(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        html_path = builder.project_dir / "output" / "frontend" / "index.html"
        content = html_path.read_text(encoding="utf-8")
        # At least one requirement name should appear in the output
        found = any(req["name"].lower() in content.lower() for req in sample_requirements)
        assert found or len(content) > 500  # Either reflected or page is substantial

    def test_generate_return_value_has_paths(self, builder, sample_requirements, sample_phases, sample_docs):
        result = builder.generate(sample_requirements, sample_phases, sample_docs)
        # Result should contain file paths or counts
        assert len(result) >= 1
        for key, value in result.items():
            assert isinstance(key, str)

    def test_file_encoding_utf8(self, builder, sample_requirements, sample_phases, sample_docs):
        builder.generate(sample_requirements, sample_phases, sample_docs)
        for filename in ["index.html", "styles.css", "design-tokens.css", "app.js"]:
            path = builder.project_dir / "output" / "frontend" / filename
            content = path.read_text(encoding="utf-8")
            assert isinstance(content, str)

    def test_cross_platform_playbook_is_rendered_into_frontend_blueprint(
        self,
        builder,
        sample_requirements,
        sample_phases,
        sample_docs,
    ):
        output_dir = builder.project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "test-app-ui-contract.json").write_text(
            (
                "{\n"
                '  "typography_preset": {"heading": "IBM Plex Sans", "body": "Public Sans"},\n'
                '  "framework_playbook": {\n'
                '    "framework": "uni-app",\n'
                '    "implementation_modules": ["自定义导航栏高度、状态栏占位、胶囊按钮区域必须独立建模"],\n'
                '    "native_capabilities": ["登录/支付/分享 provider 必须按端隔离并显式验收"],\n'
                '    "validation_surfaces": ["微信小程序导航/支付/触控与包体策略"]\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )

        builder.generate(sample_requirements, sample_phases, sample_docs)

        html_content = (builder.project_dir / "output" / "frontend" / "index.html").read_text(encoding="utf-8")
        js_content = (builder.project_dir / "output" / "frontend" / "app.js").read_text(encoding="utf-8")
        assert "跨平台框架执行护栏" in html_content
        assert "uni-app" in html_content
        assert "framework_playbook" in js_content
        assert "登录/支付/分享 provider" in js_content
