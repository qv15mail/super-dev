"""
UI 审查器 - 审查商业级 UI/UX 完成度

目标：
1. 检查 UI/UX 文档是否具备商业级设计基线
2. 检查前端源码是否偏离设计基线或出现明显 AI 模板化反模式
3. 输出可追踪的 UI 审查报告，供质量门禁与交付阶段使用
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from PIL import Image

from ..design import UIIntelligenceAdvisor

_logger = logging.getLogger("super_dev.reviewers.ui_review")


@dataclass
class UIReviewFinding:
    level: str
    title: str
    description: str
    recommendation: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "evidence": list(self.evidence),
        }


@dataclass
class UIReviewReport:
    project_name: str
    score: int
    findings: list[UIReviewFinding] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for item in self.findings if item.level == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for item in self.findings if item.level == "high")

    @property
    def medium_count(self) -> int:
        return sum(1 for item in self.findings if item.level == "medium")

    @property
    def passed(self) -> bool:
        return self.critical_count == 0 and self.score >= 80

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "score": self.score,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "passed": self.passed,
            "strengths": list(self.strengths),
            "notes": list(self.notes),
            "findings": [item.to_dict() for item in self.findings],
        }

    def to_markdown(self) -> str:
        lines = [
            f"# {self.project_name} - UI 审查报告",
            "",
            f"- **总分**: {self.score}/100",
            f"- **Critical**: {self.critical_count}",
            f"- **High**: {self.high_count}",
            f"- **Medium**: {self.medium_count}",
            f"- **结论**: {'通过' if self.passed else '需继续修正'}",
            "",
            "---",
            "",
            "## 优点",
            "",
        ]
        if self.strengths:
            lines.extend(f"- {item}" for item in self.strengths)
        else:
            lines.append("- 暂无显著优势记录。")

        lines.extend(["", "## 发现的问题", ""])
        if not self.findings:
            lines.append("- 未发现明显的商业级 UI 违例。")
        else:
            for index, finding in enumerate(self.findings, 1):
                lines.extend(
                    [
                        f"### {index}. [{finding.level.upper()}] {finding.title}",
                        "",
                        f"**问题**: {finding.description}",
                        "",
                        f"**建议**: {finding.recommendation}",
                    ]
                )
                if finding.evidence:
                    lines.extend(["", "**证据**:"])
                    lines.extend(f"- {item}" for item in finding.evidence)
                lines.append("")

        lines.extend(["## 备注", ""])
        if self.notes:
            lines.extend(f"- {item}" for item in self.notes)
        else:
            lines.append("- 无额外备注。")

        return "\n".join(lines)


class UIReviewReviewer:
    """商业级 UI 审查器"""

    MARKETING_KEYWORDS = ("hero", "testimonial", "pricing", "faq", "case study", "social proof")
    STATE_KEYWORDS = ("loading", "empty", "error", "disabled", "focus", "success")
    TOKEN_KEYWORDS = ("--color-", "--space-", "--radius-", "--shadow-", "--font-")
    DEFAULT_FONT_RE = re.compile(
        r"(font-family\s*:\s*['\"]?(inter|arial|system-ui|ui-sans-serif|sans-serif)|fontFamily\s*[:=]\s*['\"]?(Inter|Arial|system-ui))",
        re.IGNORECASE,
    )
    SUSPICIOUS_PATTERN_RE = re.compile(
        r"(purple-|pink-|bg-gradient|linear-gradient|emoji|🚀|✨|🎨|🔥|💎|🤖)",
        re.IGNORECASE,
    )

    TRUST_TERMS = (
        "testimonial",
        "case study",
        "customer",
        "clients",
        "security",
        "compliance",
        "faq",
        "review",
        "rating",
        "trusted by",
        "案例",
        "客户",
        "评价",
        "安全",
        "合规",
        "FAQ",
        "信任",
    )

    def __init__(self, project_dir: Path, name: str, tech_stack: dict[str, Any]):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack

    def review(self) -> UIReviewReport:
        findings: list[UIReviewFinding] = []
        strengths: list[str] = []
        notes: list[str] = []
        score = 100

        config = self._load_project_config()
        description = str(config.get("description") or self.name)
        frontend = str(config.get("frontend") or self.tech_stack.get("frontend") or "react")
        advisor = UIIntelligenceAdvisor()
        profile = advisor.recommend(
            description=description,
            frontend=frontend,
            product_type=self._infer_product_type(description),
            industry=self._infer_industry(description),
            style=self._infer_style(description),
        )

        uiux_path = self.project_dir / "output" / f"{self.name}-uiux.md"
        uiux_content = uiux_path.read_text(encoding="utf-8", errors="ignore") if uiux_path.exists() else ""

        source_files = self._collect_frontend_files()
        source_content = "\n".join(
            file_path.read_text(encoding="utf-8", errors="ignore")
            for file_path in source_files[:80]
        )
        preview_path = self._find_preview_file()
        preview_content = preview_path.read_text(encoding="utf-8", errors="ignore") if preview_path else ""
        preview_summary = self._inspect_preview_html(preview_content) if preview_content else {}
        screenshot_path = self._capture_preview_screenshot(preview_path) if preview_path else None
        screenshot_metrics = self._analyze_screenshot(screenshot_path) if screenshot_path else {}

        if not uiux_content:
            findings.append(
                UIReviewFinding(
                    level="high",
                    title="缺少 UI/UX 设计文档",
                    description="无法基于设计文档验证组件生态、页面骨架和信任模块。",
                    recommendation="先生成完整的 output/*-uiux.md，再进行 UI 实现和审查。",
                )
            )
            score -= 25
        else:
            required_sections = [
                "设计 Intelligence 结论",
                "组件生态与实现基线",
                "页面骨架优先级",
                "图标、图表与内容模块",
                "商业化与信任设计",
            ]
            missing_sections = [item for item in required_sections if item not in uiux_content]
            if missing_sections:
                findings.append(
                    UIReviewFinding(
                        level="high",
                        title="UI/UX 文档缺少关键商业级章节",
                        description="文档没有完整覆盖组件生态、页面骨架或信任设计，宿主难以稳定生成商业级界面。",
                        recommendation="补齐设计 intelligence、组件生态、页面骨架和信任设计章节。",
                        evidence=missing_sections,
                    )
                )
                score -= 18
            else:
                strengths.append("UI/UX 文档已覆盖组件生态、页面骨架与信任设计关键章节。")
            advanced_sections = [
                "多端适配与平台化设计策略",
                "商业级设计质量门禁",
                "精美 UI 执行工作流（Stitch 范式）",
                "组件落地清单（Tailwind / 生态组件）",
            ]
            missing_advanced = [item for item in advanced_sections if item not in uiux_content]
            if missing_advanced:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="UI/UX 文档缺少高级平台化章节",
                        description="文档缺少多端策略或质量门禁，可能导致 Web/H5/小程序/APP/桌面端 的设计一致性与商业完成度不足。",
                        recommendation="补充多端适配策略、组件库矩阵和商业级设计质量门禁章节。",
                        evidence=missing_advanced,
                    )
                )
                score -= 8
            else:
                strengths.append("UI/UX 文档已覆盖多端策略与商业级质量门禁。")
            required_platform_terms = ("WEB", "H5", "微信小程序", "APP", "桌面端")
            missing_platform_terms = [term for term in required_platform_terms if term not in uiux_content]
            if missing_platform_terms:
                findings.append(
                    UIReviewFinding(
                        level="high",
                        title="多端策略未覆盖五端口径",
                        description="UI/UX 文档未同时覆盖 Web/H5/微信小程序/APP/桌面端，平台策略存在缺口。",
                        recommendation="在跨端策略章节补齐五端目标、交互差异与共享组件契约。",
                        evidence=missing_platform_terms,
                    )
                )
                score -= 12
            else:
                strengths.append("UI/UX 文档已覆盖 Web/H5/微信小程序/APP/桌面端 五端口径。")

        expected_library = profile["primary_library"]["name"].lower()
        package_json = self._read_package_json()
        dependency_blob = json.dumps(package_json, ensure_ascii=False).lower() if package_json else ""
        if package_json:
            if "shadcn" in expected_library and not any(
                token in dependency_blob for token in ("@radix-ui", "tailwindcss", "class-variance-authority")
            ):
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="源码依赖未体现推荐组件生态",
                        description="当前推荐是 shadcn/Radix/Tailwind 体系，但依赖中没有明显对应组件生态。",
                        recommendation="检查是否已初始化推荐组件库，或在 UI/UX 文档中明确采用了替代方案。",
                        evidence=[expected_library],
                    )
                )
                score -= 8
            else:
                strengths.append(f"依赖层已基本匹配推荐组件生态：{profile['primary_library']['name']}。")
            frontend_token_expectations = {
                "miniapp": ("tdesign", "taro", "uniapp", "uni-app", "vant-weapp", "nutui"),
                "desktop": ("electron", "tauri", "wails"),
                "react-native": ("react-native", "nativewind", "tamagui"),
                "flutter": ("flutter", "dart"),
                "swiftui": ("swiftui", "xcode"),
            }
            expected_tokens = frontend_token_expectations.get(profile.get("normalized_frontend", ""))
            if expected_tokens and not any(token in dependency_blob for token in expected_tokens):
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="依赖层未体现目标端生态",
                        description="当前目标端与依赖生态不一致，可能导致交互范式与平台能力无法落地。",
                        recommendation="补齐目标端框架依赖，或在文档中声明跨端桥接方案与边界。",
                        evidence=[profile.get("normalized_frontend", "")],
                    )
                )
                score -= 8
        else:
            notes.append("未检测到 package.json，组件生态一致性仅做文档级审查。")

        if source_files:
            if not any(token in source_content for token in self.TOKEN_KEYWORDS):
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="源码中缺少明显的 design token 痕迹",
                        description="未检测到颜色、间距、字体等 token 命名，存在直接写死视觉样式的风险。",
                        recommendation="将颜色、间距、圆角、阴影和字体统一沉淀为 token / CSS variables / theme config。",
                    )
                )
                score -= 10
            else:
                strengths.append("源码中已出现 design token / CSS variables 痕迹。")

            if self.DEFAULT_FONT_RE.search(source_content) and "--font-" not in source_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="字体系统过于默认，品牌辨识度不足",
                        description="源码里出现了 Inter / Arial / system-ui 等默认字体策略，但没有明显的品牌化字体 token 或排版系统。",
                        recommendation="为商业页面定义更明确的字体体系与字号层级，不要只依赖默认 sans-serif 字体栈。",
                    )
                )
                score -= 8
            else:
                strengths.append("源码未暴露明显的默认字体依赖，排版系统更接近品牌化实现。")

            suspicious_hits = self.SUSPICIOUS_PATTERN_RE.findall(source_content)
            if suspicious_hits:
                findings.append(
                    UIReviewFinding(
                        level="high",
                        title="检测到可疑的 AI 模板化视觉痕迹",
                        description="源码中出现紫粉渐变、emoji 或过度模板化关键词，容易生成 AI 味较重的页面。",
                        recommendation="回到 UI/UX 文档规定的品牌方向，删除渐变堆砌、emoji 图标和无意义装饰。",
                        evidence=sorted({item for item in suspicious_hits})[:10],
                    )
                )
                score -= 18

            missing_state_terms = [item for item in self.STATE_KEYWORDS if item not in source_content.lower()]
            if len(missing_state_terms) >= 4:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="源码中缺少关键状态覆盖信号",
                        description="未检测到足够多的 loading / empty / error / success 等状态处理痕迹。",
                        recommendation="补齐列表、表单和关键模块的状态矩阵，不要只实现正常态。",
                        evidence=missing_state_terms[:6],
                    )
                )
                score -= 8
            else:
                strengths.append("源码中已体现出多态状态处理。")

            if any(term in description.lower() for term in ("官网", "official website", "landing", "营销")):
                marketing_hits = sum(1 for item in self.MARKETING_KEYWORDS if item in source_content.lower())
                if marketing_hits < 2:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="营销型页面缺少足够的转化与信任模块",
                            description="对外页面没有明显体现案例、FAQ、定价、评价或 social proof 模块。",
                            recommendation="补齐转化和信任模块，不要只有 Hero 和功能列表。",
                        )
                    )
                    score -= 8
                else:
                    strengths.append("营销型页面已体现出转化与信任模块。")
        else:
            notes.append("当前未检测到前端源码，仅完成文档级 UI 审查；实现后建议再次运行。")

        if preview_summary:
            if preview_summary["sections"] < 3:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="可预览页面结构过于单薄",
                        description="预览页的主结构层级不足，页面更像占位原型而不是商业级成品页面。",
                        recommendation="补齐 Hero 之外的关键模块，至少形成价值、证据、功能和下一步动作的完整结构。",
                        evidence=[f"sections={preview_summary['sections']}", f"headings={preview_summary['headings']}"],
                    )
                )
                score -= 8
            else:
                strengths.append("预览页已具备基础分区结构。")

            if preview_summary["sections"] >= 3 and preview_summary["headings"] < 3:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="页面层级不足，排版节奏偏平",
                        description="虽然页面已经拆成多个分区，但标题层级不足，信息节奏会更像占位稿而不是商业成品。",
                        recommendation="为关键分区补足 h1/h2/h3 层级与辅助文案，拉开版式节奏。",
                        evidence=[f"sections={preview_summary['sections']}", f"headings={preview_summary['headings']}"],
                    )
                )
                score -= 6

            if preview_summary["buttons"] + preview_summary["links"] < 3:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="可预览页面缺少明确交互入口",
                        description="可点击 CTA / 链接数量过少，容易形成只可观看、不可推进的静态页面。",
                        recommendation="补充核心 CTA、次级 CTA、导航或下一步动作入口。",
                    )
                )
                score -= 6

            product_type = self._infer_product_type(description)
            if product_type in {"landing", "saas", "ecommerce"}:
                if preview_summary["nav_links"] < 2:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="导航信息架构不足",
                            description="预览页导航入口过少，用户难以快速理解页面结构与主要去向。",
                            recommendation="为对外页面补齐导航层级，至少明确产品、方案、价格/案例、FAQ 或联系入口。",
                            evidence=[f"nav_links={preview_summary['nav_links']}"],
                        )
                    )
                    score -= 6

                if preview_summary["first_section_cta"] < 2:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="首屏 CTA 层级不足",
                            description="首屏只有单一动作或几乎没有动作层级，不利于转化和分流。",
                            recommendation="在首屏至少提供主 CTA 和次级 CTA，例如开始使用 + 查看演示 / 联系销售。",
                            evidence=[f"first_section_cta={preview_summary['first_section_cta']}"],
                        )
                    )
                    score -= 8

                if (
                    preview_summary["first_section_text_chars"] < 80
                    and preview_summary["first_section_media"] == 0
                ):
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="首屏信息密度不足",
                            description="首屏文案信息量偏低，且没有产品截图或媒体证据，页面容易像占位稿。",
                            recommendation="补充价值主张、辅助说明和产品证据，让首屏同时承担理解和转化任务。",
                            evidence=[
                                f"first_section_text_chars={preview_summary['first_section_text_chars']}",
                                f"first_section_media={preview_summary['first_section_media']}",
                            ],
                        )
                    )
                    score -= 8

            if preview_summary["media"] == 0 and self._infer_product_type(description) in {"landing", "saas", "ecommerce"}:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="可预览页面缺少截图或媒体证据",
                        description="营销/产品型页面没有截图、图片、视频或产品演示区域，信任与理解成本偏高。",
                        recommendation="加入产品截图、流程示意、客户案例图片或短视频演示。",
                    )
                )
                score -= 8

            if preview_summary["trust_hits"] < 2 and self._infer_product_type(description) in {"landing", "saas", "ecommerce"}:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="可预览页面信任信号不足",
                        description="预览页文本中缺少明显的案例、客户、评价、安全、FAQ 等信任模块。",
                        recommendation="为对外页面补齐信任区、FAQ、案例或安全说明。",
                        evidence=[f"trust_hits={preview_summary['trust_hits']}"],
                    )
                )
                score -= 8
            else:
                strengths.append("预览页已体现一定的信任/说明信号。")

            if preview_summary["landmarks"] < 3:
                findings.append(
                    UIReviewFinding(
                        level="low",
                        title="页面语义 landmarks 偏少",
                        description="缺少 header/main/nav/footer/section 等结构语义，后续可访问性和结构清晰度会受影响。",
                        recommendation="补充语义化结构标签，提升信息架构和可访问性基线。",
                        evidence=[f"landmarks={preview_summary['landmarks']}"],
                    )
                )
                score -= 4
        else:
            notes.append("未检测到 preview.html 或 output/frontend/index.html，未执行结构级视觉审查。")

        if screenshot_path and screenshot_metrics:
            notes.append(f"已生成预览截图: {screenshot_path}")
            if screenshot_metrics["blank_ratio"] > 0.78:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="截图显示页面留白过多",
                        description="截图中大面积为空白或浅色区域，页面可能更像占位稿而不是成熟产品页面。",
                        recommendation="补齐信息层级、模块内容和可信证据，避免只有少量文字悬浮在大背景上。",
                        evidence=[f"blank_ratio={screenshot_metrics['blank_ratio']:.2f}"],
                    )
                )
                score -= 8
            else:
                strengths.append("截图层面未出现明显的超高留白占比。")

            if screenshot_metrics["unique_colors"] < 24:
                findings.append(
                    UIReviewFinding(
                        level="low",
                        title="截图配色层次偏单薄",
                        description="截图中的有效颜色层次较少，界面可能过平、过空或缺少视觉焦点。",
                        recommendation="在保证克制的前提下，补充强调色、模块层级和更清晰的界面节奏。",
                        evidence=[f"unique_colors={screenshot_metrics['unique_colors']}"],
                    )
                )
                score -= 4

            if screenshot_metrics["accent_ratio"] < 0.006:
                findings.append(
                    UIReviewFinding(
                        level="low",
                        title="截图中缺少明显视觉焦点",
                        description="页面整体色彩变化过弱，CTA、重点模块或状态提示不够突出。",
                        recommendation="增强 CTA、标题层级、状态色和关键卡片的强调关系。",
                        evidence=[f"accent_ratio={screenshot_metrics['accent_ratio']:.4f}"],
                    )
                )
                score -= 4
            else:
                strengths.append("截图中存在一定视觉焦点和强调关系。")
        elif preview_path:
            notes.append("存在预览页，但本次未成功生成截图，已回退为结构级审查。")

        return UIReviewReport(
            project_name=self.name,
            score=max(0, score),
            findings=findings,
            strengths=strengths,
            notes=notes,
        )

    def _collect_frontend_files(self) -> list[Path]:
        allowed_suffixes = {".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte", ".css", ".scss", ".less", ".html"}
        excluded_dirs = {
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            "coverage",
        }
        files: list[Path] = []
        for path in self.project_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in allowed_suffixes:
                continue
            if any(part in excluded_dirs for part in path.parts):
                continue
            files.append(path)
        return files

    def _find_preview_file(self) -> Path | None:
        candidates = [
            self.project_dir / "preview.html",
            self.project_dir / "output" / "frontend" / "index.html",
            self.project_dir / "frontend" / "index.html",
            self.project_dir / "index.html",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _capture_preview_screenshot(self, preview_path: Path) -> Path | None:
        if os.getenv("SUPER_DEV_DISABLE_VISUAL_CAPTURE") == "1" or os.getenv("PYTEST_CURRENT_TEST"):
            return None
        if not shutil_which("npx"):
            return None

        artifact_dir = self.project_dir / "output" / "ui-review"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = artifact_dir / f"{self.name}-preview-desktop.png"
        url = preview_path.resolve().as_uri()

        cmd = [
            "npx",
            "-y",
            "playwright",
            "screenshot",
            "--device=Desktop Chrome",
            url,
            str(screenshot_path),
        ]

        try:
            subprocess.run(  # nosec B603
                cmd,
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )
        except Exception as e:
            _logger.debug(f"Failed to capture preview screenshot: {e}")
            return None

        return screenshot_path if screenshot_path.exists() else None

    def _analyze_screenshot(self, screenshot_path: Path | None) -> dict[str, float] | dict[str, int]:
        if not screenshot_path or not screenshot_path.exists():
            return {}
        try:
            with Image.open(screenshot_path) as image:
                rgb = image.convert("RGB")
                width, height = rgb.size
                sample = rgb.resize((min(220, width), min(220, height)))
                pixels = list(sample.getdata())
        except Exception as e:
            _logger.debug(f"Failed to analyze screenshot: {e}")
            return {}

        if not pixels:
            return {}

        blank_pixels = 0
        accent_pixels = 0
        reduced = []
        for r, g, b in pixels:
            brightness = (r + g + b) / 3
            spread = max(r, g, b) - min(r, g, b)
            if brightness > 235 and spread < 16:
                blank_pixels += 1
            if spread > 60 and 35 < brightness < 220:
                accent_pixels += 1
            reduced.append((r // 32, g // 32, b // 32))

        total = len(pixels)
        return {
            "blank_ratio": blank_pixels / total,
            "accent_ratio": accent_pixels / total,
            "unique_colors": len(set(reduced)),
        }

    def _read_package_json(self) -> dict[str, Any] | None:
        for candidate in (self.project_dir / "package.json", self.project_dir / "frontend" / "package.json"):
            if candidate.exists():
                return json.loads(candidate.read_text(encoding="utf-8"))
        return None

    def _load_project_config(self) -> dict[str, Any]:
        config_path = self.project_dir / "super-dev.yaml"
        if not config_path.exists():
            return {}
        try:
            import yaml  # type: ignore[import-untyped]

            return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            _logger.debug(f"Failed to load project config: {e}")
            return {}

    def _infer_product_type(self, description: str) -> str:
        text = description.lower()
        if any(word in text for word in ["dashboard", "仪表盘", "后台", "admin", "工作台", "workspace"]):
            return "dashboard"
        if any(word in text for word in ["landing", "落地页", "营销页", "官网", "official website"]):
            return "landing"
        if any(word in text for word in ["saas", "平台", "platform", "软件服务"]):
            return "saas"
        if any(word in text for word in ["商城", "电商", "store", "shop", "checkout"]):
            return "ecommerce"
        if any(word in text for word in ["博客", "内容", "blog", "cms", "文档"]):
            return "content"
        return "general"

    def _infer_industry(self, description: str) -> str:
        text = description.lower()
        if any(word in text for word in ["医疗", "健康", "health", "medical", "care"]):
            return "healthcare"
        if any(word in text for word in ["金融", "支付", "bank", "fintech", "结算"]):
            return "fintech"
        if any(word in text for word in ["教育", "培训", "education", "learning"]):
            return "education"
        if any(word in text for word in ["法律", "法务", "legal", "律师"]):
            return "legal"
        if any(word in text for word in ["政务", "government", "public"]):
            return "government"
        if any(word in text for word in ["美容", "美业", "wellness", "beauty", "spa"]):
            return "beauty"
        return "general"

    def _infer_style(self, description: str) -> str:
        text = description.lower()
        if any(word in text for word in ["极简", "minimal", "简约"]):
            return "minimal"
        if any(word in text for word in ["专业", "商务", "professional", "business"]):
            return "professional"
        if any(word in text for word in ["活泼", "playful", "fun"]):
            return "playful"
        if any(word in text for word in ["奢华", "premium", "luxury", "高端"]):
            return "luxury"
        return "modern"

    def _inspect_preview_html(self, html: str) -> dict[str, int]:
        parser = _HTMLSurfaceParser(self.TRUST_TERMS)
        parser.feed(html)
        parser.close()
        return parser.summary()


class _HTMLSurfaceParser(HTMLParser):
    """轻量 HTML 结构审查器"""

    def __init__(self, trust_terms: tuple[str, ...]):
        super().__init__()
        self.trust_terms = tuple(item.lower() for item in trust_terms)
        self.sections = 0
        self.headings = 0
        self.buttons = 0
        self.links = 0
        self.media = 0
        self.landmarks = 0
        self.nav_links = 0
        self._nav_depth = 0
        self._section_index = 0
        self._section_depth = 0
        self.first_section_text_chars = 0
        self.first_section_cta = 0
        self.first_section_media = 0
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered_tag = tag.lower()
        if lowered_tag in {"section", "article", "aside"}:
            self.sections += 1
            self._section_depth += 1
            if self._section_depth == 1:
                self._section_index += 1
        if lowered_tag in {"h1", "h2", "h3"}:
            self.headings += 1
        if lowered_tag == "button":
            self.buttons += 1
            if self._section_index == 1:
                self.first_section_cta += 1
        if lowered_tag == "a":
            self.links += 1
            if self._nav_depth > 0:
                self.nav_links += 1
            if self._section_index == 1:
                self.first_section_cta += 1
        if lowered_tag in {"img", "picture", "video", "figure", "svg"}:
            self.media += 1
            if self._section_index == 1:
                self.first_section_media += 1
        if lowered_tag in {"header", "main", "nav", "footer", "section"}:
            self.landmarks += 1
        if lowered_tag == "nav":
            self._nav_depth += 1

    def handle_endtag(self, tag: str) -> None:
        lowered_tag = tag.lower()
        if lowered_tag in {"section", "article", "aside"} and self._section_depth > 0:
            self._section_depth -= 1
            if self._section_depth == 0 and self._section_index == 1:
                self._section_index = 99
        if lowered_tag == "nav" and self._nav_depth > 0:
            self._nav_depth -= 1

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self._text_parts.append(text.lower())
            if self._section_index == 1:
                self.first_section_text_chars += len(text)

    def summary(self) -> dict[str, int]:
        text_blob = " ".join(self._text_parts)
        trust_hits = sum(1 for item in self.trust_terms if item in text_blob)
        return {
            "sections": self.sections,
            "headings": self.headings,
            "buttons": self.buttons,
            "links": self.links,
            "media": self.media,
            "landmarks": self.landmarks,
            "nav_links": self.nav_links,
            "first_section_text_chars": self.first_section_text_chars,
            "first_section_cta": self.first_section_cta,
            "first_section_media": self.first_section_media,
            "trust_hits": trust_hits,
        }


def shutil_which(command: str) -> str | None:
    try:
        import shutil

        return shutil.which(command)
    except Exception as e:
        _logger.debug(f"Failed to check command availability for {command}: {e}")
        return None
