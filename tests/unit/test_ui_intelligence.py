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
            "# site\n\n## 设计 Intelligence 结论\n\n## 组件生态与实现基线\n\n## 页面骨架优先级\n\n## 图标、图表与内容模块\n\n## 商业化与信任设计\n",
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

        assert report.score > 70
        assert any("预览页已具备基础分区结构" in item for item in report.strengths)

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
