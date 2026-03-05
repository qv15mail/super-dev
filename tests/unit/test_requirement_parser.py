"""
需求解析与前端骨架测试
"""

from pathlib import Path

from super_dev.creators.document_generator import DocumentGenerator
from super_dev.creators.frontend_builder import FrontendScaffoldBuilder
from super_dev.creators.requirement_parser import RequirementParser


class TestRequirementParser:
    def test_parse_requirements_by_keywords(self):
        parser = RequirementParser()
        requirements = parser.parse_requirements("做一个支持登录和搜索筛选的数据平台")

        spec_names = {item["spec_name"] for item in requirements}
        assert "core" in spec_names
        assert "auth" in spec_names
        assert "search" in spec_names

    def test_parse_requirements_fallback(self):
        parser = RequirementParser()
        requirements = parser.parse_requirements("构建一个特别的新产品")

        spec_names = {item["spec_name"] for item in requirements}
        assert "experience" in spec_names
        assert "operation" in spec_names

    def test_detect_scenario(self, temp_project_dir: Path):
        parser = RequirementParser()

        assert parser.detect_scenario(temp_project_dir) == "0-1"

        (temp_project_dir / "src").mkdir()
        assert parser.detect_scenario(temp_project_dir) == "1-N+1"


class TestDocumentGeneratorIntegration:
    def test_document_generator_extracts_dynamic_requirements(self):
        generator = DocumentGenerator(
            name="payment-app",
            description="支付系统需要通知中心和账单功能",
            frontend="react",
            backend="node",
        )

        requirements = generator.extract_requirements()
        names = {req["spec_name"] for req in requirements}
        assert "billing" in names
        assert "notification" in names

    def test_document_generator_includes_language_preferences(self):
        generator = DocumentGenerator(
            name="polyglot-platform",
            description="构建支持多端协作的智能平台",
            frontend="react",
            backend="python",
            language_preferences=["python", "typescript", "rust"],
        )

        language_line = "Python / TypeScript / Rust"
        assert language_line in generator.generate_prd()
        assert language_line in generator.generate_architecture()
        assert language_line in generator.generate_uiux()


class TestFrontendScaffoldBuilder:
    def test_generate_frontend_scaffold(self, temp_project_dir: Path):
        builder = FrontendScaffoldBuilder(
            project_dir=temp_project_dir,
            name="demo-app",
            description="一个可演示的需求驱动平台",
            frontend="react",
        )

        result = builder.generate(
            requirements=[
                {
                    "spec_name": "core",
                    "req_name": "business-core-flow",
                    "description": "核心业务流程",
                    "scenarios": [],
                }
            ],
            phases=[
                {
                    "id": "phase-1",
                    "title": "需求对齐与文档冻结",
                    "objective": "冻结文档版本",
                    "deliverables": ["PRD", "架构", "UIUX"],
                }
            ],
            docs={
                "prd": str(temp_project_dir / "output" / "demo-prd.md"),
                "architecture": str(temp_project_dir / "output" / "demo-architecture.md"),
                "uiux": str(temp_project_dir / "output" / "demo-uiux.md"),
                "plan": str(temp_project_dir / "output" / "demo-plan.md"),
                "frontend_blueprint": str(temp_project_dir / "output" / "demo-frontend-blueprint.md"),
            },
        )

        html_path = Path(result["html"])
        css_path = Path(result["css"])
        js_path = Path(result["js"])

        assert html_path.exists()
        assert css_path.exists()
        assert js_path.exists()
        assert "demo-app" in html_path.read_text(encoding="utf-8")
        assert "--primary" in css_path.read_text(encoding="utf-8")
        assert "business-core-flow" in js_path.read_text(encoding="utf-8")
