from pathlib import Path

from PIL import Image

from super_dev.design import UIIntelligenceAdvisor
from super_dev.reviewers.ui_review import UIReviewReviewer


class TestUIIntelligenceAdvisor:
    def test_recommend_react_dashboard_stack(self):
        advisor = UIIntelligenceAdvisor()

        profile = advisor.recommend(
            description="构建一个金融数据分析工作台和运营后台",
            frontend="react",
            product_type="dashboard",
            industry="fintech",
            style="professional",
        )

        assert profile["primary_library"]["name"] == "shadcn/ui + Radix UI + Tailwind CSS"
        assert "TanStack Table" in profile["component_stack"]["table"]
        assert "安全" in "".join(profile["trust_modules"])
        assert any("后台" in item or "营销页" in item for item in profile["banned_patterns"])
        assert any("DaisyUI" in item["name"] or "Aceternity" in item["name"] for item in profile["alternative_libraries"])
        assert any(row["scene"] == "微信小程序" for row in profile["ui_library_matrix"])
        assert len(profile["quality_checklist"]) >= 4

    def test_recommend_vue_stack_prefers_naive_ui(self):
        advisor = UIIntelligenceAdvisor()

        profile = advisor.recommend(
            description="企业协作 SaaS 平台",
            frontend="vue",
            product_type="saas",
            industry="general",
            style="modern",
        )

        assert profile["primary_library"]["name"] == "Naive UI + Tailwind CSS"
        assert profile["component_stack"]["form"] == "vee-validate + Zod / Valibot"

    def test_recommend_miniprogram_stack_prefers_tdesign(self):
        advisor = UIIntelligenceAdvisor()

        profile = advisor.recommend(
            description="微信小程序会员商城与下单流程",
            frontend="taro",
            product_type="ecommerce",
            industry="general",
            style="modern",
        )

        assert profile["normalized_frontend"] == "miniapp"
        assert "TDesign 小程序" in profile["primary_library"]["name"]
        assert "小程序" in profile["component_stack"]["form"]

    def test_recommend_desktop_stack_prefers_electron_tauri(self):
        advisor = UIIntelligenceAdvisor()

        profile = advisor.recommend(
            description="桌面端数据分析客户端，支持离线与本地文件导入",
            frontend="electron",
            product_type="dashboard",
            industry="general",
            style="professional",
        )

        assert profile["normalized_frontend"] == "desktop"
        assert "Electron / Tauri" in profile["primary_library"]["name"]
        assert "AG Grid" in profile["component_stack"]["table"]


class TestUIReviewReviewer:
    def test_review_detects_missing_uiux_sections(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-uiux.md").write_text("# demo uiux", encoding="utf-8")

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        assert report.score < 100
        assert any("缺少关键商业级章节" in item.title for item in report.findings)

    def test_review_uses_preview_surface_signals(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "site-uiux.md").write_text(
            "# site\n\n## 设计 Intelligence 结论\n\n## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n\n## 多端适配与平台化设计策略\n\n## 商业级设计质量门禁\n\n## 精美 UI 执行工作流（Stitch 范式）\n\n## 组件落地清单（Tailwind / 生态组件）\n\nWEB\nH5\n微信小程序\nAPP\n桌面端\n",
            encoding="utf-8",
        )
        (temp_project_dir / "preview.html").write_text(
            """
<!doctype html>
<html>
  <body>
    <header><nav><a href="#pricing">Pricing</a></nav></header>
    <main>
      <section><h1>Commercial Product</h1><button>Start Free</button><img src="hero.png" alt="hero" /></section>
      <section><h2>Case Study</h2><p>Trusted by enterprise customers with security and compliance.</p></section>
      <section><h2>FAQ</h2><a href="#faq">View FAQ</a></section>
    </main>
    <footer></footer>
  </body>
</html>
""",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="site",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        assert report.score > 40
        assert any("预览页已具备基础分区结构" in item for item in report.strengths)
        assert report.alignment_summary["layout_shell"]["passed"] is True
        assert report.alignment_summary["navigation_shell"]["passed"] is True
        assert report.alignment_summary["banned_patterns"]["passed"] is True
        # 验证 UI/UX 专家视角检查已注入
        expert_findings = [f for f in report.findings if f.title.startswith("[UI 专家]") or f.title.startswith("[UX 专家]")]
        assert len(expert_findings) > 0, "UI/UX 专家视角检查应产生至少一项发现"

    def test_review_flags_generic_typography_and_flat_hierarchy(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "brand-uiux.md").write_text(
            "# brand\n\n## 设计 Intelligence 结论\n\n## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n",
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "styles.css").write_text(
            "body { font-family: Inter, Arial, system-ui, sans-serif; }",
            encoding="utf-8",
        )
        (temp_project_dir / "preview.html").write_text(
            """
<!doctype html>
<html>
  <body>
    <header><nav><a href="#hero">Home</a></nav></header>
    <main>
      <section><h1>Brand</h1><button>Start</button></section>
      <section><p>Evidence</p></section>
      <section><p>Pricing</p></section>
    </main>
    <footer></footer>
  </body>
</html>
""",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="brand",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("字体系统过于默认" in title for title in titles)
        assert any("页面层级不足" in title for title in titles)

    def test_review_flags_weak_hero_conversion_signals(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "landing-uiux.md").write_text(
            "# landing\n\n## 设计 Intelligence 结论\n\n## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n",
            encoding="utf-8",
        )
        (temp_project_dir / "preview.html").write_text(
            """
<!doctype html>
<html>
  <body>
    <header><nav><a href="#hero">Home</a></nav></header>
    <main>
      <section><h1>Launch faster</h1><button>Start</button></section>
      <section><h2>Features</h2><p>Feature list</p></section>
      <section><h2>FAQ</h2><p>Answers</p></section>
    </main>
    <footer></footer>
  </body>
</html>
""",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="landing",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("导航信息架构不足" in title for title in titles)
        assert any("首屏 CTA 层级不足" in title for title in titles)
        assert any("首屏信息密度不足" in title for title in titles)

    def test_review_flags_emoji_icons_and_claude_like_shell(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "ops-uiux.md").write_text(
            (
                "# ops\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 可信、稳定、业务优先\n"
                "**字体组合**: Manrope / Source Sans 3\n"
                "**配色逻辑**: Fintech Blue（主色 #2563EB / 强调色 #0EA5E9）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            """
export function App() {
  return (
    <div className="conversation-shell chat-sidebar">
      <aside className="thread-list">History</aside>
      <main>
        <button>✨ 保存</button>
        <div className="assistant-message">hello</div>
      </main>
    </div>
  );
}
""",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="ops",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("emoji 功能图标" in title for title in titles)
        assert any("Claude / 聊天式产品骨架复刻痕迹" in title for title in titles)
        assert report.alignment_summary["layout_shell"]["passed"] is False
        assert report.alignment_summary["navigation_shell"]["passed"] is False
        assert report.alignment_summary["banned_patterns"]["passed"] is False

    def test_review_flags_uiux_frozen_icon_system_not_reflected_in_source(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "brand-uiux.md").write_text(
            (
                "# brand\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 现代商业产品基线，品牌感与效率并重\n"
                "**字体组合**: Manrope / Source Sans 3\n"
                "**配色逻辑**: General SaaS（主色 #2563EB / 强调色 #14B8A6）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"@heroicons/react":"^2.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            "export function App(){ return <div><span>Save</span></div>; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="brand",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("图标系统" in title for title in titles)

    def test_review_flags_uiux_frozen_font_pair_not_reflected_in_source(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "fonts-uiux.md").write_text(
            (
                "# fonts\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 可信、稳定、业务优先\n"
                "**字体组合**: IBM Plex Sans / Public Sans\n"
                "**配色逻辑**: Fintech Blue（主色 #2563EB / 强调色 #14B8A6）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"lucide-react":"^0.1.0","@radix-ui/react-dialog":"^1.0.0","tailwindcss":"^3.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "styles.css").write_text(
            "body { font-family: Inter, Arial, system-ui, sans-serif; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="fonts",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("字体组合" in title for title in titles)

    def test_review_flags_ui_contract_tokens_not_wired_into_source(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        frontend_output = output_dir / "frontend"
        output_dir.mkdir(parents=True, exist_ok=True)
        frontend_output.mkdir(parents=True, exist_ok=True)
        (output_dir / "contract-uiux.md").write_text(
            (
                "# contract\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 编辑感、品牌化、商业完成度优先\n"
                "**字体组合**: Space Grotesk / Inter\n"
                "**配色逻辑**: Editorial Blue（主色 #0F172A / 强调色 #2563EB）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (output_dir / "contract-ui-contract.json").write_text(
            (
                "{\n"
                '  "icon_system": "Lucide Icons",\n'
                '  "emoji_policy": {"allowed_in_ui": false, "allowed_as_icon": false, "allowed_during_development": false},\n'
                '  "typography_preset": {"heading": "Space Grotesk", "body": "Inter"},\n'
                '  "ui_library_preference": {"final_selected": "shadcn/ui + Radix UI + Tailwind CSS"},\n'
                '  "design_tokens": {"css_variables": ":root { --color-primary: #0F172A; --font-heading: \\"Space Grotesk\\"; }"}\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        (frontend_output / "design-tokens.css").write_text(
            ":root { --color-primary: #0F172A; --font-heading: 'Space Grotesk'; }\n",
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"lucide-react":"^0.1.0","@radix-ui/react-dialog":"^1.0.0","tailwindcss":"^3.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            "export function App(){ return <main className='bg-slate-950 text-white'>Hello</main>; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="contract",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("Design Token 接入实现" in title for title in titles)

    def test_review_accepts_magic_ui_when_ui_contract_selects_it(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        frontend_output = output_dir / "frontend"
        output_dir.mkdir(parents=True, exist_ok=True)
        frontend_output.mkdir(parents=True, exist_ok=True)
        (output_dir / "magic-uiux.md").write_text(
            (
                "# magic\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 展示增强、品牌驱动、轻动效\n"
                "**字体组合**: Sora / Inter\n"
                "**配色逻辑**: Midnight Contrast（主色 #111827 / 强调色 #22C55E）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: Magic UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (output_dir / "magic-ui-contract.json").write_text(
            (
                "{\n"
                '  "icon_system": "Lucide Icons",\n'
                '  "emoji_policy": {"allowed_in_ui": false, "allowed_as_icon": false, "allowed_during_development": false},\n'
                '  "typography_preset": {"heading": "Sora", "body": "Inter"},\n'
                '  "ui_library_preference": {"final_selected": "Magic UI + Tailwind CSS"},\n'
                '  "design_tokens": {"css_variables": ":root { --color-primary: #111827; --font-heading: \\"Sora\\"; }"}\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        (frontend_output / "design-tokens.css").write_text(
            ":root { --color-primary: #111827; --font-heading: 'Sora'; }\n",
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"magicui":"^1.0.0","lucide-react":"^0.1.0","tailwindcss":"^3.0.0","framer-motion":"^11.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            "import 'output/frontend/design-tokens.css';\nimport { MagicCard } from 'magicui';\nexport function App(){ return <main style={{color:'var(--color-primary)'}}><MagicCard>Magic</MagicCard></main>; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="magic",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert not any("组件生态" in title for title in titles)

    def test_review_flags_component_import_drift_when_dependency_exists_but_source_not_using_contract(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        frontend_output = output_dir / "frontend"
        output_dir.mkdir(parents=True, exist_ok=True)
        frontend_output.mkdir(parents=True, exist_ok=True)
        (output_dir / "imports-uiux.md").write_text(
            (
                "# imports\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 可信、稳定、业务优先\n"
                "**字体组合**: IBM Plex Sans / Public Sans\n"
                "**配色逻辑**: Fintech Blue（主色 #2563EB / 强调色 #14B8A6）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (output_dir / "imports-ui-contract.json").write_text(
            (
                "{\n"
                '  "icon_system": "Lucide Icons",\n'
                '  "emoji_policy": {"allowed_in_ui": false, "allowed_as_icon": false, "allowed_during_development": false},\n'
                '  "typography_preset": {"heading": "IBM Plex Sans", "body": "Public Sans"},\n'
                '  "ui_library_preference": {"final_selected": "shadcn/ui + Radix UI + Tailwind CSS"},\n'
                '  "design_tokens": {"css_variables": ":root { --color-primary: #2563EB; }"}\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        (frontend_output / "design-tokens.css").write_text(
            ":root { --color-primary: #2563EB; }\n",
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"lucide-react":"^0.1.0","@radix-ui/react-dialog":"^1.0.0","tailwindcss":"^3.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            "import './styles.css';\nimport { Button } from '@/components/common/Button';\nexport function App(){ return <main style={{color:'var(--color-primary)'}}><Button>Ready</Button></main>; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="imports",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("源码 import 未落实冻结组件生态" in title for title in titles)
        assert report.alignment_summary["component_ecosystem"]["passed"] is True
        assert report.alignment_summary["component_imports"]["passed"] is False

    def test_review_flags_missing_theme_entry_and_navigation_shell(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        frontend_output = output_dir / "frontend"
        output_dir.mkdir(parents=True, exist_ok=True)
        frontend_output.mkdir(parents=True, exist_ok=True)
        (output_dir / "shell-uiux.md").write_text(
            (
                "# shell\n\n## 设计 Intelligence 结论\n\n"
                "**主视觉气质**: 可信、稳定、业务优先\n"
                "**字体组合**: IBM Plex Sans / Public Sans\n"
                "**配色逻辑**: Fintech Blue（主色 #2563EB / 强调色 #14B8A6）\n"
                "**图标系统**: Lucide Icons\n"
                "**首选组件生态**: shadcn/ui + Radix UI + Tailwind CSS\n"
                "## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n"
            ),
            encoding="utf-8",
        )
        (output_dir / "shell-ui-contract.json").write_text(
            (
                "{\n"
                '  "icon_system": "Lucide Icons",\n'
                '  "emoji_policy": {"allowed_in_ui": false, "allowed_as_icon": false, "allowed_during_development": false},\n'
                '  "typography_preset": {"heading": "IBM Plex Sans", "body": "Public Sans"},\n'
                '  "ui_library_preference": {"final_selected": "shadcn/ui + Radix UI + Tailwind CSS"},\n'
                '  "design_tokens": {"css_variables": ":root { --color-primary: #2563EB; }"}\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        (frontend_output / "design-tokens.css").write_text(
            ":root { --color-primary: #2563EB; }\n",
            encoding="utf-8",
        )
        (temp_project_dir / "package.json").write_text(
            '{"dependencies":{"lucide-react":"^0.1.0","@radix-ui/react-dialog":"^1.0.0","tailwindcss":"^3.0.0"}}',
            encoding="utf-8",
        )
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        (frontend_dir / "App.tsx").write_text(
            "export function App(){ return <main><section>Dashboard</section></main>; }",
            encoding="utf-8",
        )

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="shell",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        report = reviewer.review()

        titles = [item.title for item in report.findings]
        assert any("主题入口" in title for title in titles)
        assert any("导航骨架" in title for title in titles)
        assert report.alignment_summary["theme_entry"]["passed"] is False
        assert report.alignment_summary["navigation_shell"]["passed"] is False

    def test_screenshot_analysis_extracts_visual_metrics(self, temp_project_dir: Path):
        image_path = temp_project_dir / "shot.png"
        image = Image.new("RGB", (120, 80), "#ffffff")
        for x in range(20, 100):
            for y in range(20, 60):
                image.putpixel((x, y), (15, 124, 250))
        image.save(image_path)

        reviewer = UIReviewReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node", "platform": "web"},
        )
        metrics = reviewer._analyze_screenshot(image_path)

        assert metrics["blank_ratio"] < 1
        assert metrics["accent_ratio"] > 0
        assert metrics["unique_colors"] >= 2
