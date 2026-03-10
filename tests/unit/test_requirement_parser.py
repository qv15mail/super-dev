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

    def test_detect_request_mode(self):
        parser = RequirementParser()

        assert parser.detect_request_mode("修复登录接口报错并补充回归验证") == "bugfix"
        assert parser.detect_request_mode("开发一个新的商业官网") == "feature"


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

    def test_document_generator_includes_richer_commercial_sections(self):
        generator = DocumentGenerator(
            name="delivery-grade-app",
            description="构建一个面向企业协作的商业级工作台",
            frontend="react",
            backend="python",
        )

        prd = generator.generate_prd()
        architecture = generator.generate_architecture()
        uiux = generator.generate_uiux()

        assert "### 1.4 市场与对标结论" in prd
        assert "### 1.6 需求澄清问题" in prd
        assert "### 2.4 功能优先级与范围边界" in prd
        assert "### 7.4 业务验收矩阵" in prd
        assert "### 1.3 需求到架构的落地映射" in architecture
        assert "### 3.3 关键时序图" in architecture
        assert "### 8.3 容错与降级策略" in architecture
        assert "### 1.4 商业级体验目标" in uiux
        assert "### 1.5 设计 Intelligence 结论" in uiux
        assert "### 2.7 组件生态与实现基线" in uiux
        assert "### 5.3 组件状态矩阵" in uiux
        assert "### 5.4 图标、图表与内容模块" in uiux
        assert "### 7.3 商业化与信任设计" in uiux

    def test_document_generator_embeds_ui_intelligence_stack(self):
        generator = DocumentGenerator(
            name="official-site",
            description="为一个商业级 SaaS 产品生成官方网站和产品页",
            frontend="react",
            backend="node",
        )

        uiux = generator.generate_uiux()

        assert "shadcn/ui + Radix UI + Tailwind CSS" in uiux
        assert "表单与验证" in uiux
        assert "图标体系" in uiux

    def test_execution_plan_switches_to_bugfix_mode(self):
        generator = DocumentGenerator(
            name="hotfix-patch",
            description="修复支付回调重复扣款 bug，并补充回归验证",
            frontend="react",
            backend="python",
        )

        plan = generator.generate_execution_plan(scenario="1-N+1")

        assert "> **请求模式**: bugfix" in plan
        assert "问题复现与影响分析" in plan
        assert "轻量文档冻结" in plan


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
