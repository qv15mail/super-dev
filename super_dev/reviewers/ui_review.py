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
    alignment_summary: dict[str, Any] = field(default_factory=dict)

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
            "alignment_summary": dict(self.alignment_summary),
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

        if self.alignment_summary:
            lines.extend(["", "## UI 契约对齐摘���", ""])
            for item in self._alignment_markdown_lines():
                lines.append(f"- {item}")

        # UI/UX 专家视角章节
        expert_findings = [f for f in self.findings if f.title.startswith("[UI 专家]") or f.title.startswith("[UX 专家]")]
        if expert_findings:
            lines.extend(["", "## UI/UX ��家视角", ""])
            ui_items = [f for f in expert_findings if f.title.startswith("[UI 专家]")]
            ux_items = [f for f in expert_findings if f.title.startswith("[UX 专家]")]
            if ui_items:
                lines.append("### UI 专家 (设计Token/品牌一致性/组件状态/反AI模板)")
                lines.append("")
                for item in ui_items:
                    marker = item.level.upper()
                    lines.append(f"- [{marker}] {item.title.replace('[UI 专家] ', '')}: {item.description}")
                lines.append("")
            if ux_items:
                lines.append("### UX 专家 (用户旅程/导航层级/表单设计/可访问性)")
                lines.append("")
                for item in ux_items:
                    marker = item.level.upper()
                    lines.append(f"- [{marker}] {item.title.replace('[UX 专家] ', '')}: {item.description}")
                lines.append("")

        return "\n".join(lines)

    def alignment_markdown(self) -> str:
        lines = [
            f"# {self.project_name} - UI 契约对齐报告",
            "",
        ]
        for item in self._alignment_markdown_lines():
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)

    def _alignment_markdown_lines(self) -> list[str]:
        items: list[str] = []
        for key, value in self.alignment_summary.items():
            if isinstance(value, dict):
                passed = value.get("passed")
                expected = value.get("expected")
                observed = value.get("observed")
                label = value.get("label", key)
                status = "ok" if passed else "gap"
                if expected or observed:
                    items.append(f"{label}: {status} | expected={expected or '-'} | observed={observed or '-'}")
                else:
                    items.append(f"{label}: {status}")
            else:
                items.append(f"{key}: {value}")
        return items


class UIReviewReviewer:
    """商业级 UI 审查器"""

    MARKETING_KEYWORDS = ("hero", "testimonial", "pricing", "faq", "case study", "social proof")
    STATE_KEYWORDS = ("loading", "empty", "error", "disabled", "focus", "success")
    TOKEN_KEYWORDS = ("--color-", "--space-", "--radius-", "--shadow-", "--font-")
    DEFAULT_FONT_RE = re.compile(
        r"(font-family\s*:\s*['\"]?(inter|arial|system-ui|ui-sans-serif|sans-serif)|fontFamily\s*[:=]\s*['\"]?(Inter|Arial|system-ui))",
        re.IGNORECASE,
    )
    HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    EMOJI_RE = re.compile(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]")
    SUSPICIOUS_PATTERN_RE = re.compile(
        r"(purple-|pink-|bg-gradient|linear-gradient|emoji|🚀|✨|🎨|🔥|💎|🤖)",
        re.IGNORECASE,
    )
    CLAUDE_CLONE_RE = re.compile(
        r"(anthropic|claude|chat-sidebar|conversation-list|thread-list|assistant-message|model-selector|conversation-shell|chat-shell)",
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

    UIUX_DECISION_PATTERNS = {
        "style_direction": re.compile(r"\*\*主视觉气质\*\*:\s*(.+)"),
        "font_pair": re.compile(r"\*\*字体组合\*\*:\s*(.+)"),
        "color_logic": re.compile(r"\*\*配色逻辑\*\*:\s*(.+)"),
        "icon_system": re.compile(r"\*\*图标系统\*\*:\s*(.+)"),
        "primary_library": re.compile(r"\*\*首选组件生态\*\*:\s*(.+)"),
    }

    def __init__(self, project_dir: Path, name: str, tech_stack: dict[str, Any]):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack

        # 加载 UI / UX 专家工具箱
        try:
            from ..experts.toolkit import load_expert_toolkits

            toolkits = load_expert_toolkits()
            self._ui_toolkit = toolkits.get("UI")
            self._ux_toolkit = toolkits.get("UX")
        except Exception:
            self._ui_toolkit = None
            self._ux_toolkit = None

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

        # 从 UI/UX 专家工具箱提取检查维度
        ui_expert_dimensions = self._collect_expert_review_dimensions("UI", "frontend")
        ux_expert_dimensions = self._collect_expert_review_dimensions("UX", "frontend")

        uiux_path = self.project_dir / "output" / f"{self.name}-uiux.md"
        uiux_content = uiux_path.read_text(encoding="utf-8", errors="ignore") if uiux_path.exists() else ""
        uiux_decisions = self._extract_uiux_decisions(uiux_content)
        ui_contract = self._load_ui_contract()

        source_files = self._collect_frontend_files()
        source_content = "\n".join(
            file_path.read_text(encoding="utf-8", errors="ignore")
            for file_path in source_files[:80]
        )
        preview_path = self._find_preview_file()
        preview_content = preview_path.read_text(encoding="utf-8", errors="ignore") if preview_path else ""
        combined_visual_content = "\n".join([uiux_content, source_content, preview_content])
        preview_summary = self._inspect_preview_html(preview_content) if preview_content else {}
        screenshot_path = self._capture_preview_screenshot(preview_path) if preview_path else None
        screenshot_metrics = self._analyze_screenshot(screenshot_path) if screenshot_path else {}
        design_tokens_path = self.project_dir / "output" / "frontend" / "design-tokens.css"
        design_tokens_content = (
            design_tokens_path.read_text(encoding="utf-8", errors="ignore") if design_tokens_path.exists() else ""
        )
        alignment_summary: dict[str, Any] = {
            "ui_contract": {
                "label": "UI 契约文件",
                "passed": bool(ui_contract),
                "expected": "output/*-ui-contract.json",
                "observed": str(self.project_dir / "output" / f"{self.name}-ui-contract.json") if ui_contract else "",
            }
        }
        product_type = self._infer_product_type(description)
        conversational_product = any(
            token in description.lower() for token in ("ai", "chat", "对话", "助手", "agent", "copilot")
        )

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
            ui_decision_markers = [
                "主视觉气质",
                "字体组合",
                "配色逻辑",
                "图标系统",
                "Design Token 冻结输出",
                "备选实现路径",
            ]
            missing_decision_markers = [item for item in ui_decision_markers if item not in uiux_content]
            if missing_decision_markers:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="UI 系统决策未被完整冻结",
                        description="UI/UX 文档仍像描述性说明，缺少明确的风格、字体、配色、图标和 token 冻结结果，宿主容易回退到模板化默认输出。",
                        recommendation="在 UI/UX 文档里补齐主视觉气质、字体组合、配色逻辑、图标系统、Design Token 冻结输出和备选方案取舍。",
                        evidence=missing_decision_markers[:6],
                    )
                )
                score -= 8
            elif "2 个视觉方向候选" not in uiux_content and "主方案 + 备选方案" not in uiux_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="UI 文档缺少双方案取舍约束",
                        description="文档没有强制记录主方案与备选方案的取舍，宿主容易滑向单一路径并反复输出同一种页面风格。",
                        recommendation="要求关键页面至少提供 2 个视觉方向候选，并写明为什么采用主方案、为什么放弃备选方案。",
                    )
                )
                score -= 6
            else:
                strengths.append("UI/UX 文档已冻结风格决策、token 与备选方案取舍。")
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

        selected_library = self._resolve_primary_library(ui_contract, uiux_decisions)
        expected_library = (selected_library or profile.get("primary_library", {}).get("name", "")).lower()
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
                strengths.append(f"依赖层已基本匹配推荐组件生态：{selected_library or profile['primary_library']['name']}。")
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

            icon_system = self._resolve_contract_or_doc_value(
                contract=ui_contract,
                decisions=uiux_decisions,
                contract_key="icon_system",
                decision_key="icon_system",
            )
            expected_icon_tokens = self._expected_icon_tokens(icon_system)
            if expected_icon_tokens:
                icon_aligned = any(token in dependency_blob or token in source_content.lower() for token in expected_icon_tokens)
                alignment_summary["icon_system"] = {
                    "label": "图标系统",
                    "passed": icon_aligned,
                    "expected": icon_system,
                    "observed": ", ".join(expected_icon_tokens),
                }
                if not icon_aligned:
                    findings.append(
                        UIReviewFinding(
                            level="high",
                            title="源码未落实文档冻结的图标系统",
                            description="UI/UX 文档已经冻结图标系统，但源码和依赖里没有对应图标库痕迹，宿主很容易退回 emoji、默认图标或随手混用多个图标来源。",
                            recommendation="把文档里声明的图标库真正接入依赖和组件实现，并删除与该图标系统无关的临时图标写法。",
                            evidence=[icon_system],
                        )
                    )
                    score -= 12
                else:
                    strengths.append(f"源码已体现文档冻结的图标系统：{icon_system}。")

            font_pair = self._resolve_font_pair(ui_contract, uiux_decisions)
            expected_font_tokens = self._expected_font_tokens(font_pair)
            if expected_font_tokens:
                source_visual_content = "\n".join([source_content, preview_content]).lower()
                matched_fonts = [token for token in expected_font_tokens if token in source_visual_content]
                alignment_summary["font_pair"] = {
                    "label": "字体组合",
                    "passed": bool(matched_fonts),
                    "expected": font_pair,
                    "observed": ", ".join(matched_fonts),
                }
                if not matched_fonts and self.DEFAULT_FONT_RE.search(source_content):
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="源码未落实文档冻结的字体组合",
                            description="UI/UX 文档已经冻结字体组合，但源码仍然停留在默认字体或没有接入目标字体，品牌差异化会被宿主默认实现冲掉。",
                            recommendation="在字体导入、CSS variables、Tailwind theme 或全局样式里接入文档声明的字体组合，并消除默认字体兜底对主视觉的影响。",
                            evidence=[font_pair],
                        )
                    )
                    score -= 8

            primary_library = selected_library
            expected_library_tokens = self._expected_library_tokens(primary_library)
            library_aligned = any(
                token in dependency_blob or token in source_content.lower() for token in expected_library_tokens
            ) if expected_library_tokens else False
            if expected_library_tokens:
                alignment_summary["component_ecosystem"] = {
                    "label": "组件生态",
                    "passed": library_aligned,
                    "expected": primary_library,
                    "observed": ", ".join(expected_library_tokens),
                }
            if expected_library_tokens and not library_aligned:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="源码未落实文档冻结的组件生态",
                        description="UI/UX 文档已经冻结了首选组件生态，但源码和依赖没有体现这条主方案，宿主容易在实现阶段再次漂移到其他 UI 体系。",
                        recommendation="让 package 依赖、组件 import 和实现基线与文档声明的组件生态保持一致；如果改用备选方案，必须先回写 UI/UX 文档。",
                        evidence=[primary_library],
                    )
                )
                score -= 8

            expected_import_tokens = self._expected_component_import_tokens(primary_library)
            import_sources = self._extract_import_sources(source_content)
            matched_imports = [
                token
                for token in import_sources
                if any(expected in token for expected in expected_import_tokens)
            ]
            should_enforce_component_imports = bool(package_json) and bool(expected_import_tokens)
            if expected_import_tokens:
                alignment_summary["component_imports"] = {
                    "label": "组件导入路径",
                    "passed": bool(matched_imports) if should_enforce_component_imports else True,
                    "expected": ", ".join(expected_import_tokens),
                    "observed": (
                        ", ".join(matched_imports[:8])
                        if matched_imports
                        else ("not enforced for static scaffold" if not should_enforce_component_imports else "")
                    ),
                }
            if should_enforce_component_imports and not matched_imports and source_files:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="源码 import 未落实冻结组件生态",
                        description="依赖层可能已经安装了目标组件生态，但源码导入路径没有体现这条主方案，说明宿主在实现阶段仍可能回退到临时组件或默认 HTML。",
                        recommendation="让页面和组件真正从冻结后的组件生态导入实现；如果改用其他组件体系，先回写 UI/UX 文档和 UI 契约。",
                        evidence=[primary_library, *expected_import_tokens[:4]],
                    )
                )
                score -= 8

            if ui_contract:
                design_token_reference_ready = self._has_design_token_contract_wiring(
                    source_content=source_content,
                    preview_content=preview_content,
                    design_tokens_content=design_tokens_content,
                )
                theme_entry_ready = self._has_theme_entry_contract_wiring(
                    source_content=source_content,
                    preview_content=preview_content,
                    design_tokens_content=design_tokens_content,
                )
                alignment_summary["theme_entry"] = {
                    "label": "主题入口",
                    "passed": theme_entry_ready,
                    "expected": "全局主题入口或 design token 入口已接入",
                    "observed": "theme provider / design tokens wired" if theme_entry_ready else "",
                }
                if not theme_entry_ready:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="源码缺少主题入口或全局主题接线",
                            description="虽然已经冻结了 UI 契约，但源码里看不到明显的主题入口、ThemeProvider、全局 design token 接线或主题配置，后续页面很容易各写各的。",
                            recommendation="在应用入口或全局 layout 中接入 design-tokens.css、ThemeProvider、Tailwind theme 或等价的主题配置，确保页面共用同一套视觉基线。",
                            evidence=["missing global theme entry / provider / token import"],
                        )
                    )
                    score -= 8
                alignment_summary["design_tokens"] = {
                    "label": "Design Token 接入",
                    "passed": design_token_reference_ready,
                    "expected": str(design_tokens_path),
                    "observed": "design-tokens.css / CSS variables wired" if design_token_reference_ready else "",
                }
                if not design_token_reference_ready:
                    findings.append(
                        UIReviewFinding(
                            level="high",
                            title="源码未把 UI 契约的 Design Token 接入实现",
                            description="虽然已经生成了 UI 契约，但源码和预览页没有明确体现 design-tokens.css 或 CSS variables 的接入，宿主仍可能在实现阶段直接写死视觉样式。",
                            recommendation="确保前端入口显式接入 design-tokens.css，并在组件和样式中优先使用 var(--color-*) / var(--space-*) / var(--font-*) 等 token。",
                            evidence=[
                                str(design_tokens_path) if design_tokens_path.exists() else "design-tokens.css missing",
                                "missing design token reference in source or preview",
                            ],
                        )
                    )
                    score -= 14
                else:
                    strengths.append("源码已显式接入 UI 契约对应的 design tokens。")

                token_variables = self._extract_token_variables(design_tokens_content)
                if token_variables:
                    referenced = [token for token in token_variables if token in source_content or token in preview_content]
                    alignment_summary["token_usage"] = {
                        "label": "冻结 Token 使用率",
                        "passed": len(referenced) >= min(2, len(token_variables)),
                        "expected": ", ".join(token_variables[:6]),
                        "observed": ", ".join(referenced[:6]),
                    }
                    if len(referenced) < min(2, len(token_variables)):
                        findings.append(
                            UIReviewFinding(
                                level="medium",
                                title="源码对冻结 Token 的实际使用偏弱",
                                description="Design Token 文件虽然存在，但源码里很少看到对应变量被真正使用，说明 UI 系统可能只停留在生成文件层而没有进入组件实现。",
                                recommendation="让布局、标题、卡片、按钮和状态组件优先使用冻结后的 color/space/font token，而不是继续写死数值。",
                                evidence=token_variables[:6],
                            )
                        )
                        score -= 8

                hardcoded_hex_colors = sorted({item for item in self.HEX_COLOR_RE.findall(source_content)})[:12]
                if hardcoded_hex_colors and "var(--color-" not in source_content and "--color-" not in design_tokens_content:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="源码仍以硬编码颜色为主，UI 契约执行不足",
                            description="前端源码里出现了多处硬编码色值，但没有明显的 color token 使用痕迹，UI 系统的颜色策略尚未真正进入实现。",
                            recommendation="将主要颜色迁移到 design-tokens.css / theme 配置，并让组件优先消费 token 变量。",
                            evidence=hardcoded_hex_colors,
                        )
                    )
                    score -= 8

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

            emoji_hits = sorted({item for item in self.EMOJI_RE.findall(combined_visual_content)})[:10]
            if emoji_hits:
                findings.append(
                    UIReviewFinding(
                        level="critical",
                        title="检测到 emoji 功能图标或表情占位",
                        description="UI 产物中出现 emoji 字符，说明图标系统没有在开始阶段被锁定，已违反 Super Dev 的 UI 硬约束。",
                        recommendation="删除所有 emoji 字符，改用 Lucide / Heroicons / Tabler / 官方组件图标，并在 UI/UX 文档里明确图标库与替换策略。",
                        evidence=emoji_hits,
                    )
                )
                score -= 24

            clone_hits = sorted({item for item in self.CLAUDE_CLONE_RE.findall(source_content)})[:10]
            if preview_summary or source_files:
                expected_layout = "非聊天壳层，按产品类型组织导航、主体内容和关键动作"
                observed_layout_parts = []
                nav_markers = self._extract_navigation_shell_markers(source_content)
                if preview_summary:
                    observed_layout_parts.extend(
                        [
                            f"sections={preview_summary['sections']}",
                            f"headings={preview_summary['headings']}",
                            f"nav_links={preview_summary['nav_links']}",
                            f"first_section_cta={preview_summary['first_section_cta']}",
                        ]
                    )
                if nav_markers:
                    observed_layout_parts.append(f"source_nav={', '.join(nav_markers[:6])}")
                if clone_hits and not conversational_product:
                    observed_layout_parts.append("chat-shell pattern detected")
                layout_shell_passed = True
                if clone_hits and not conversational_product:
                    layout_shell_passed = False
                elif preview_summary:
                    if product_type in {"landing", "saas", "ecommerce"}:
                        layout_shell_passed = (
                            preview_summary["sections"] >= 3
                            and preview_summary["nav_links"] >= 2
                            and preview_summary["first_section_cta"] >= 2
                        )
                    else:
                        layout_shell_passed = (
                            preview_summary["sections"] >= 2 and preview_summary["headings"] >= 2
                        )
                alignment_summary["layout_shell"] = {
                    "label": "页面骨架",
                    "passed": layout_shell_passed,
                    "expected": expected_layout,
                    "observed": " | ".join(observed_layout_parts),
                }
                navigation_shell_passed = bool(nav_markers) or bool(preview_summary.get("nav_links", 0))
                if clone_hits and not conversational_product:
                    navigation_shell_passed = False
                elif product_type in {"dashboard", "saas"}:
                    navigation_shell_passed = navigation_shell_passed and (
                        any(marker in nav_markers for marker in ("sidebar", "topbar", "header", "nav", "breadcrumb", "appshell"))
                        or bool(preview_summary.get("nav_links", 0))
                    )
                alignment_summary["navigation_shell"] = {
                    "label": "导航骨架",
                    "passed": navigation_shell_passed,
                    "expected": "源码或预览中存在导航 / header / sidebar / breadcrumb 等骨架信号",
                    "observed": " | ".join(observed_layout_parts),
                }
                if not navigation_shell_passed:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="源码缺少稳定的导航骨架",
                            description="源码和预览里没有足够明确的导航、header、sidebar 或 breadcrumb 信号，页面容易退化成只堆内容的单块界面。",
                            recommendation="为当前产品类型补齐稳定的导航骨架，在源码入口明确 header/nav/sidebar/breadcrumb 等结构，而不是只靠内容块临时拼接。",
                            evidence=nav_markers[:6] or [f"preview_nav_links={preview_summary.get('nav_links', 0)}"],
                        )
                    )
                    score -= 8
            if clone_hits and not conversational_product:
                findings.append(
                    UIReviewFinding(
                        level="high",
                        title="检测到 Claude / 聊天式产品骨架复刻痕迹",
                        description="当前产品不是对话式 AI，但源码仍然出现了 Claude/聊天壳层相关模式，容易导致页面同质化成 Claude 风格。",
                        recommendation="回到 UI/UX 文档，重做页面骨架、导航结构、字体组合和品牌配色，不要复用聊天产品外壳。",
                        evidence=clone_hits,
                    )
                )
                score -= 18

            banned_hits = []
            if suspicious_hits:
                banned_hits.extend(sorted({item for item in suspicious_hits}))
            if emoji_hits:
                banned_hits.extend(emoji_hits)
            if clone_hits and not conversational_product:
                banned_hits.extend(clone_hits)
            alignment_summary["banned_patterns"] = {
                "label": "反模式约束",
                "passed": len(banned_hits) == 0,
                "expected": "无 emoji 图标、无 Claude 聊天壳层、无模板化渐变/关键词",
                "observed": ", ".join(banned_hits[:10]),
            }

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

            product_type = self._infer_product_type(description)
            if preview_summary["trust_hits"] < 2 and product_type in {"landing", "saas", "ecommerce"}:
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
            elif preview_summary["trust_hits"] >= 2:
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

        # UI/UX 专家视角检查
        expert_perspective_findings = self._run_expert_perspective_checks(
            source_content=source_content,
            preview_content=preview_content,
            uiux_content=uiux_content,
            ui_expert_dimensions=ui_expert_dimensions,
            ux_expert_dimensions=ux_expert_dimensions,
        )
        for epf in expert_perspective_findings:
            findings.append(epf)
            if epf.level == "high":
                score -= 6
            elif epf.level == "medium":
                score -= 4

        return UIReviewReport(
            project_name=self.name,
            score=max(0, min(100, score)),
            findings=findings,
            strengths=strengths,
            notes=notes,
            alignment_summary=alignment_summary,
        )

    # ------------------------------------------------------------------
    # UI/UX 专家视角
    # ------------------------------------------------------------------

    def _collect_expert_review_dimensions(self, role: str, phase: str) -> list[str]:
        """从专家工具箱提取指定角色在指定阶段的审查维度。"""
        toolkit = self._ui_toolkit if role == "UI" else self._ux_toolkit
        if toolkit is None:
            return []
        try:
            return toolkit.get_review_checklist(phase)
        except Exception:
            return []

    def _run_expert_perspective_checks(
        self,
        *,
        source_content: str,
        preview_content: str,
        uiux_content: str,
        ui_expert_dimensions: list[str],
        ux_expert_dimensions: list[str],
    ) -> list[UIReviewFinding]:
        """基于 UI/UX 专家工具箱的检查维度生成额外审查发现。

        UI 专家关注：设计 Token 系统、品牌一致性、组件状态完整性、反 AI 模板感
        UX 专家关注：用户旅程、导航层级、表单设计、可访问性
        """
        findings: list[UIReviewFinding] = []
        combined = "\n".join([source_content, preview_content]).lower()

        if not source_content and not preview_content:
            return findings

        # --- UI 专家维度 ---
        if ui_expert_dimensions:
            # 设计 Token 系统完整性
            token_categories = {
                "color": ("--color-", "color-primary", "color-secondary", "color-accent"),
                "space": ("--space-", "spacing-", "gap-", "padding-"),
                "font": ("--font-", "font-size-", "font-weight-", "line-height-"),
                "radius": ("--radius-", "border-radius-", "rounded-"),
                "shadow": ("--shadow-", "box-shadow-", "shadow-"),
            }
            missing_categories = [
                cat for cat, tokens in token_categories.items()
                if not any(t in combined for t in tokens)
            ]
            if len(missing_categories) >= 3:
                findings.append(
                    UIReviewFinding(
                        level="high",
                        title="[UI 专家] Token 体系覆盖不完整",
                        description=(
                            "UI 专家要求 Token 体系覆盖颜色/字体/间距/圆角/阴影五大类，"
                            f"当前缺失 {len(missing_categories)} 类。"
                        ),
                        recommendation="按 UI 专家规范补齐缺失的 Token 类别，确保组件复用同一套视觉变量。",
                        evidence=[f"缺失: {', '.join(missing_categories)}"],
                    )
                )

            # 品牌一致性：检查是否存在多套不一致的视觉系统
            brand_signals = ("brand", "logo", "primary", "accent", "--color-brand", "theme")
            brand_hits = sum(1 for s in brand_signals if s in combined)
            if brand_hits == 0 and source_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UI 专家] 品牌识别信号缺失",
                        description="源码和预览中缺少品牌色、Logo 引用或主题标识，产品辨识度不足。",
                        recommendation="在全局样式或 Token 层定义品牌主色、辅助色和 Logo 使用规范。",
                    )
                )

            # 组件状态完整性（UI 专家更严格的标准）
            ui_state_keywords = ("hover", "focus", "active", "disabled", "loading", "error", "empty", "success")
            covered_states = [kw for kw in ui_state_keywords if kw in combined]
            if len(covered_states) < 4 and source_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UI 专家] 组件状态矩阵不齐全",
                        description=(
                            f"UI 专家要求组件覆盖 hover/focus/loading/empty/error/disabled 等状态，"
                            f"当前仅检测到 {len(covered_states)} 种。"
                        ),
                        recommendation="为核心交互组件补齐状态样式，确保每种状态都有明确的视觉反馈。",
                        evidence=[f"已覆盖: {', '.join(covered_states) or '无'}"],
                    )
                )

            # 反 AI 模板感（UI 专家的补充检查）
            ai_template_signals = (
                "bg-gradient-to-r from-purple",
                "bg-gradient-to-br from-pink",
                "animate-pulse",
                "animate-bounce",
                "backdrop-blur",
            )
            ai_hits = [s for s in ai_template_signals if s in combined]
            if len(ai_hits) >= 2:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UI 专家] AI 模板化视觉痕迹偏重",
                        description="检测到多个 AI 常见模板化样式叠加，界面容易失去品牌差异化。",
                        recommendation="删除堆砌的渐变和动画效果，回归设计文档规定的品牌方向。",
                        evidence=ai_hits[:6],
                    )
                )

        # --- UX 专家维度 ---
        if ux_expert_dimensions:
            # 用户旅程：检查核心任务流信号
            journey_signals = (
                "onboarding", "wizard", "stepper", "step-",
                "progress", "breadcrumb", "flow", "funnel",
                "引导", "步骤", "流程",
            )
            journey_hits = sum(1 for s in journey_signals if s in combined)
            if journey_hits == 0 and source_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UX 专家] 缺少用户旅程引导信号",
                        description="UX 专家要求核心任务流有清晰的步骤引导，但源码中缺少 onboarding、stepper、progress 等信号。",
                        recommendation="为关键任务流加入步骤指示器、进度条或面包屑导航，降低用户认知负荷。",
                    )
                )

            # 导航层级：检测导航深度
            deep_nav_signals = ("sub-subnav", "nested-dropdown", "三级菜单", "deep-nav")
            has_deep_nav = any(s in combined for s in deep_nav_signals)
            if has_deep_nav:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UX 专家] 导航层级可能超过 3 层",
                        description="UX 专家要求导航层级不超过 3 层，检测到深层嵌套导航信号。",
                        recommendation="精简导航结构，将深层页面通过搜索、标签或快捷入口替代多层级嵌套。",
                    )
                )

            # 表单设计：检查表单验证和错误处理
            form_signals = ("form", "<form", "input", "textarea", "select")
            has_forms = any(s in combined for s in form_signals)
            if has_forms:
                validation_signals = (
                    "validation", "validate", "error-message", "field-error",
                    "invalid", "required", "pattern=", "helpertext",
                    "errormessage", "formerror",
                )
                has_validation = any(s in combined for s in validation_signals)
                if not has_validation:
                    findings.append(
                        UIReviewFinding(
                            level="medium",
                            title="[UX 专家] 表单缺少验证与错误恢复机制",
                            description="UX 专家要求表单具备实时验证和错误恢复指引，但未检测到明显的验证逻辑。",
                            recommendation="为表单字段添加实时校验、错误提示和恢复引导，减少用户填写挫败感。",
                        )
                    )

            # 可访问性：检查 WCAG 基础信号
            a11y_signals = (
                "aria-", "role=", "sr-only", "screen-reader",
                "alt=", "tabindex", "focus-visible", "focus-trap",
                "labelledby", "describedby",
            )
            a11y_hits = sum(1 for s in a11y_signals if s in combined)
            if a11y_hits < 2 and source_content:
                findings.append(
                    UIReviewFinding(
                        level="medium",
                        title="[UX 专家] 可访问性基线不足",
                        description=(
                            "UX 专家要求满足 WCAG 2.1 AA 标准，但源码中缺少足够的 "
                            "aria 属性、role 标注或 focus 管理信号。"
                        ),
                        recommendation="为交互元素添加 aria-label、role 属性，确保键盘导航和屏幕阅读器可用。",
                        evidence=[f"a11y 信号数: {a11y_hits}"],
                    )
                )

        return findings

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
                try:
                    return json.loads(candidate.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    return None
        return None

    def _load_ui_contract(self) -> dict[str, Any]:
        contract_path = self.project_dir / "output" / f"{self.name}-ui-contract.json"
        if not contract_path.exists():
            return {}
        try:
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.debug(f"Failed to parse UI contract: {e}")
            return {}
        return payload if isinstance(payload, dict) else {}

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

    def _extract_uiux_decisions(self, uiux_content: str) -> dict[str, str]:
        decisions: dict[str, str] = {}
        for key, pattern in self.UIUX_DECISION_PATTERNS.items():
            match = pattern.search(uiux_content)
            if not match:
                continue
            decisions[key] = match.group(1).strip()
        return decisions

    def _resolve_contract_or_doc_value(
        self,
        *,
        contract: dict[str, Any],
        decisions: dict[str, str],
        contract_key: str,
        decision_key: str,
    ) -> str:
        contract_value = contract.get(contract_key)
        if isinstance(contract_value, str) and contract_value.strip():
            return contract_value.strip()
        if contract_key == "icon_system":
            component_stack = contract.get("component_stack")
            if isinstance(component_stack, dict):
                nested_icon_system = component_stack.get("icon") or component_stack.get("icons")
                if isinstance(nested_icon_system, str) and nested_icon_system.strip():
                    return nested_icon_system.strip()
        return decisions.get(decision_key, "")

    def _resolve_font_pair(self, contract: dict[str, Any], decisions: dict[str, str]) -> str:
        typography = contract.get("typography_preset")
        if isinstance(typography, dict):
            heading = str(typography.get("heading", "")).strip()
            body = str(typography.get("body", "")).strip()
            if heading or body:
                return " / ".join(item for item in [heading, body] if item)
        return decisions.get("font_pair", "")

    def _resolve_primary_library(self, contract: dict[str, Any], decisions: dict[str, str]) -> str:
        preference = contract.get("ui_library_preference")
        if isinstance(preference, dict):
            selected = str(preference.get("final_selected", "")).strip()
            if selected:
                return selected
        primary = contract.get("primary_library")
        if isinstance(primary, dict):
            name = str(primary.get("name", "")).strip()
            if name:
                return name
        return decisions.get("primary_library", "")

    def _has_design_token_contract_wiring(
        self,
        *,
        source_content: str,
        preview_content: str,
        design_tokens_content: str,
    ) -> bool:
        combined = "\n".join([source_content, preview_content]).lower()
        if "design-tokens.css" in combined:
            return True
        if "var(--color-" in combined or "var(--space-" in combined or "var(--font-" in combined:
            return True
        if design_tokens_content and ("--color-" in design_tokens_content or "--font-" in design_tokens_content):
            return "var(--" in combined
        return False

    def _has_theme_entry_contract_wiring(
        self,
        *,
        source_content: str,
        preview_content: str,
        design_tokens_content: str,
    ) -> bool:
        combined = "\n".join([source_content, preview_content]).lower()
        theme_signals = (
            "themeprovider",
            "configprovider",
            "cssvarsprovider",
            "chakraprovider",
            "mantineprovider",
            "vuetify",
            "createTheme".lower(),
            "theme=",
            "data-theme",
            "design-tokens.css",
        )
        if any(signal in combined for signal in theme_signals):
            return True
        if "--color-" in design_tokens_content or "--font-" in design_tokens_content:
            return "var(--" in combined
        return False

    def _extract_navigation_shell_markers(self, source_content: str) -> list[str]:
        if not source_content:
            return []
        lowered = source_content.lower()
        candidates = (
            ("<nav", "nav"),
            ("<header", "header"),
            ("<aside", "aside"),
            ("sidebar", "sidebar"),
            ("topbar", "topbar"),
            ("breadcrumb", "breadcrumb"),
            ("appshell", "appshell"),
            ("navigationmenu", "navigationmenu"),
            ("menubar", "menubar"),
        )
        found: list[str] = []
        for needle, label in candidates:
            if needle in lowered and label not in found:
                found.append(label)
        return found

    def _extract_token_variables(self, design_tokens_content: str) -> list[str]:
        if not design_tokens_content:
            return []
        matches = re.findall(r"(--(?:color|space|font|radius|shadow)-[a-z0-9-]+)\s*:", design_tokens_content, flags=re.IGNORECASE)
        ordered = []
        seen: set[str] = set()
        for item in matches:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
        return ordered

    def _expected_icon_tokens(self, icon_system: str) -> tuple[str, ...]:
        lowered = icon_system.lower()
        if "lucide" in lowered:
            return ("lucide", "@lucide", "lucide-react", "lucide-vue", "lucide-svelte")
        if "heroicons" in lowered:
            return ("heroicons", "@heroicons")
        if "tabler" in lowered:
            return ("tabler", "@tabler")
        if "phosphor" in lowered:
            return ("phosphor", "@phosphor")
        if "tdesign" in lowered:
            return ("tdesign-icons", "tdesign")
        return ()

    def _expected_font_tokens(self, font_pair: str) -> tuple[str, ...]:
        parts = []
        for item in font_pair.split("/"):
            token = item.strip().lower().replace("  ", " ")
            token = token.replace("-", " ")
            if token:
                parts.append(token)
        return tuple(parts)

    def _expected_library_tokens(self, primary_library: str) -> tuple[str, ...]:
        lowered = primary_library.lower()
        if "shadcn" in lowered or "radix" in lowered:
            return ("@radix-ui", "shadcn", "class-variance-authority", "tailwindcss")
        if "magic ui" in lowered:
            return ("magicui", "magic ui", "motion", "framer-motion")
        if "aceternity" in lowered:
            return ("aceternity", "framer-motion", "motion")
        if "daisyui" in lowered:
            return ("daisyui", "tailwindcss")
        if "headless ui" in lowered:
            return ("@headlessui", "headlessui", "tailwindcss")
        if "nextui" in lowered or "heroui" in lowered:
            return ("@nextui-org", "@heroui", "nextui", "heroui")
        if "tremor" in lowered:
            return ("@tremor", "tremor")
        if "naive ui" in lowered:
            return ("naive-ui",)
        if "tdesign" in lowered:
            return ("tdesign",)
        if "chakra" in lowered:
            return ("@chakra-ui",)
        if "ant design" in lowered or "antd" in lowered:
            return ("antd", "@ant-design")
        if "vuetify" in lowered:
            return ("vuetify",)
        return ()

    def _expected_component_import_tokens(self, primary_library: str) -> tuple[str, ...]:
        lowered = primary_library.lower()
        if "shadcn" in lowered or "radix" in lowered:
            return ("@/components/ui", "/components/ui/", "components/ui/", "@radix-ui")
        if "magic ui" in lowered:
            return ("magicui", "@/components/magicui", "/components/magicui/", "components/magicui/")
        if "aceternity" in lowered:
            return ("aceternity", "@/components/ui", "/components/ui/")
        if "daisyui" in lowered:
            return ("daisyui",)
        if "headless ui" in lowered:
            return ("@headlessui",)
        if "nextui" in lowered or "heroui" in lowered:
            return ("@nextui-org", "@heroui")
        if "tremor" in lowered:
            return ("@tremor",)
        if "naive ui" in lowered:
            return ("naive-ui",)
        if "tdesign" in lowered:
            return ("tdesign",)
        if "chakra" in lowered:
            return ("@chakra-ui",)
        if "ant design" in lowered or "antd" in lowered:
            return ("antd", "@ant-design")
        if "vuetify" in lowered:
            return ("vuetify",)
        return ()

    def _extract_import_sources(self, source_content: str) -> list[str]:
        if not source_content:
            return []
        matches = re.findall(r"(?:from\s+['\"]([^'\"]+)['\"]|import\s+['\"]([^'\"]+)['\"])", source_content)
        imports: list[str] = []
        seen: set[str] = set()
        for left, right in matches:
            value = (left or right or "").strip().lower()
            if not value or value in seen:
                continue
            seen.add(value)
            imports.append(value)
        return imports


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
