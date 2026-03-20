from pathlib import Path

import yaml

from super_dev.creators.prompt_generator import AIPromptGenerator


class TestAIPromptGenerator:
    def test_generate_requires_research_and_commercial_ui(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-research.md").write_text("# research\n同类产品研究", encoding="utf-8")
        (output_dir / "demo-prd.md").write_text("# prd", encoding="utf-8")
        (output_dir / "demo-architecture.md").write_text("# architecture", encoding="utf-8")
        (output_dir / "demo-uiux.md").write_text("# uiux", encoding="utf-8")
        (output_dir / "demo-execution-plan.md").write_text("# plan", encoding="utf-8")
        (output_dir / "demo-frontend-blueprint.md").write_text("# frontend blueprint", encoding="utf-8")
        (temp_project_dir / ".super-dev").mkdir(parents=True, exist_ok=True)
        (temp_project_dir / ".super-dev" / "WORKFLOW.md").write_text("# workflow", encoding="utf-8")
        (output_dir / "demo-bootstrap.md").write_text("# bootstrap", encoding="utf-8")

        config = {
            "description": "构建商业级协作工作台",
            "platform": "web",
            "frontend": "react",
            "backend": "python",
        }
        (temp_project_dir / "super-dev.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

        generator = AIPromptGenerator(project_dir=temp_project_dir, name="demo")
        prompt = generator.generate()

        assert "阶段 0. 同类产品研究" in prompt
        assert "宿主原生联网 / browse / search" in prompt
        assert "output/demo-research.md" in prompt
        assert "knowledge/" in prompt
        assert "output/knowledge-cache/demo-knowledge-bundle.json" in prompt
        assert "knowledge_application_plan" in prompt
        assert "必须按其中的阶段应用计划使用本地知识" in prompt
        assert "首轮响应契约（首次触发必须执行）" in prompt
        assert "Super Dev` 流水线已激活" in prompt
        assert ".super-dev/WORKFLOW.md" in prompt
        assert "output/demo-bootstrap.md" in prompt
        assert "当前阶段是 `research`" in prompt
        assert "三份核心文档完成后会暂停等待用户确认" in prompt
        assert "阶段 1.5. 文档确认门（强制暂停）" in prompt
        assert "未经用户明确确认，不得创建 `.super-dev/changes/*`" in prompt
        assert "阶段 3. 前端优先实现并运行验证" in prompt
        assert "商业级 UI/UX 强制规则" in prompt
        assert "UI 达到商业级完成度而不是模板化页面" in prompt
        assert "本项目 UI 实现基线" in prompt
        assert "首选组件生态" in prompt
        assert "宿主 UI 生成执行契约（必须遵守）" in prompt
        assert "每个关键页面必须提供 **2 个视觉方案**" in prompt
        assert "Token → Primitive → Pattern → Surface" in prompt
        assert "非技术与专业用户都能使用同一套交互" in prompt
        assert "Web/H5/微信小程序/APP/桌面端" in prompt
        assert "TDesign 小程序 / RN / Flutter / SwiftUI / Electron / Tauri" in prompt

    def test_generate_bugfix_prompt_requires_lightweight_docs(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        for suffix in ("research", "prd", "architecture", "uiux", "execution-plan", "frontend-blueprint"):
            (output_dir / f"demo-{suffix}.md").write_text(f"# {suffix}", encoding="utf-8")

        config = {
            "description": "修复登录接口报错并补充回归测试",
            "platform": "web",
            "frontend": "react",
            "backend": "python",
        }
        (temp_project_dir / "super-dev.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

        generator = AIPromptGenerator(project_dir=temp_project_dir, name="demo")
        prompt = generator.generate()

        assert "如果当前任务属于缺陷修复 / bugfix / 回归修复，也不得跳过文档与验证" in prompt
        assert "如果当前需求明显属于 bugfix / regression / hotfix" in prompt
        assert "阶段 4.8. 缺陷修复轻量路径（仅 bugfix 场景）" in prompt
        assert "- `bugfix`" in prompt
