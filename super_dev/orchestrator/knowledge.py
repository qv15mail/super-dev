# -*- coding: utf-8 -*-
"""
知识增强模块

将用户输入需求通过「本地知识库 + 联网检索」进行增强，
为后续 PRD / 架构 / UIUX / Spec 生成提供更完整上下文。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class KnowledgeItem:
    """知识项"""

    source: str
    title: str
    snippet: str
    link: str = ""
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "snippet": self.snippet,
            "link": self.link,
            "score": self.score,
        }


class KnowledgeAugmenter:
    """需求知识增强器"""

    _STOPWORDS = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "from",
        "this",
        "功能",
        "项目",
        "系统",
        "需要",
        "支持",
        "实现",
        "一个",
        "需求",
    }

    def __init__(self, project_dir: Path, web_enabled: bool = True):
        self.project_dir = Path(project_dir).resolve()
        self.web_enabled = web_enabled
        self.docs_dir = self.project_dir / "docs"
        self.specs_dir = self.project_dir / ".super-dev" / "specs"
        self.data_dir = self.project_dir / "super_dev" / "data"
        self.builtin_data_dir = Path(__file__).resolve().parents[1] / "data"

    def augment(
        self,
        requirement: str,
        domain: str = "",
        max_local_results: int = 8,
        max_web_results: int = 5,
    ) -> dict[str, Any]:
        """对需求做知识增强"""
        query = requirement.strip()
        keywords = self._extract_keywords(query)

        local_items = self._collect_local_items(
            keywords=keywords,
            max_results=max_local_results,
        )
        web_items = self._collect_web_items(
            query=self._build_web_query(query, domain),
            max_results=max_web_results,
        )

        enriched_requirement = self._compose_enriched_requirement(
            requirement=requirement,
            local_items=local_items,
            web_items=web_items,
        )

        return {
            "original_requirement": requirement,
            "domain": domain,
            "keywords": keywords,
            "local_knowledge": [item.to_dict() for item in local_items],
            "web_knowledge": [item.to_dict() for item in web_items],
            "enriched_requirement": enriched_requirement,
        }

    def to_markdown(self, bundle: dict[str, Any]) -> str:
        """将增强结果渲染为 Markdown 报告"""
        lines = [
            "# 需求增强报告",
            "",
            f"**原始需求**: {bundle.get('original_requirement', '')}",
            f"**领域**: {bundle.get('domain', 'general') or 'general'}",
            "",
            "## 提取关键词",
            "",
            ", ".join(bundle.get("keywords", [])) or "(none)",
            "",
            "## 本地知识库结果",
            "",
        ]

        local_items = bundle.get("local_knowledge", [])
        if not local_items:
            lines.append("- 未命中本地知识。")
        else:
            for item in local_items:
                title = item.get("title", "unknown")
                snippet = item.get("snippet", "")
                lines.append(f"- **{title}** ({item.get('source', 'local')}): {snippet}")
        lines.append("")

        lines.extend(["## 联网检索结果", ""])
        web_items = bundle.get("web_knowledge", [])
        if not web_items:
            lines.append("- 未获得联网结果（可能网络受限或无匹配结果）。")
        else:
            for item in web_items:
                title = item.get("title", "unknown")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                link_text = f" [{link}]({link})" if link else ""
                lines.append(f"- **{title}**: {snippet}{link_text}")
        lines.append("")

        lines.extend(
            [
                "## 增强后的需求描述",
                "",
                bundle.get("enriched_requirement", bundle.get("original_requirement", "")),
                "",
            ]
        )
        return "\n".join(lines)

    def _extract_keywords(self, text: str) -> list[str]:
        tokens = re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]{2,}", text.lower())
        expanded: list[str] = []
        for token in tokens:
            expanded.append(token)
            # 对纯中文短句追加 2 字滑窗关键词，提升匹配率
            if re.fullmatch(r"[\u4e00-\u9fff]{3,}", token):
                for i in range(len(token) - 1):
                    expanded.append(token[i : i + 2])

        unique: list[str] = []
        for token in expanded:
            if token in self._STOPWORDS:
                continue
            if token not in unique:
                unique.append(token)
        return unique[:12]

    def _iter_local_files(self) -> list[Path]:
        files: list[Path] = []
        if self.docs_dir.exists():
            files.extend(self.docs_dir.rglob("*.md"))
        if self.specs_dir.exists():
            files.extend(self.specs_dir.rglob("*.md"))
        if self.data_dir.exists():
            files.extend(self.data_dir.rglob("*.csv"))
        if self.builtin_data_dir.exists() and self.builtin_data_dir != self.data_dir:
            files.extend(self.builtin_data_dir.rglob("*.csv"))
        return files

    def _collect_local_items(self, keywords: list[str], max_results: int) -> list[KnowledgeItem]:
        if not keywords:
            return []

        items: list[KnowledgeItem] = []
        for file_path in self._iter_local_files():
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lowered = content.lower()
            score = 0.0
            for keyword in keywords:
                if keyword in lowered:
                    score += 1.0
            if score <= 0:
                continue

            snippet = self._first_matching_snippet(content, keywords)
            items.append(
                KnowledgeItem(
                    source=self._format_source_path(file_path),
                    title=file_path.stem,
                    snippet=snippet,
                    score=score,
                )
            )

        items.sort(key=lambda item: item.score, reverse=True)
        return items[:max_results]

    def _first_matching_snippet(self, content: str, keywords: list[str]) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines:
            lowered = line.lower()
            if any(keyword in lowered for keyword in keywords):
                return line[:220]
        return (lines[0][:220] if lines else "")

    def _format_source_path(self, file_path: Path) -> str:
        try:
            return str(file_path.relative_to(self.project_dir))
        except ValueError:
            try:
                return f"builtin/{file_path.relative_to(self.builtin_data_dir)}"
            except ValueError:
                return str(file_path)

    def _build_web_query(self, requirement: str, domain: str) -> str:
        if domain:
            return f"{requirement} {domain} best practices architecture ui ux"
        return f"{requirement} best practices architecture ui ux"

    def _collect_web_items(self, query: str, max_results: int) -> list[KnowledgeItem]:
        if not self.web_enabled:
            return []

        try:
            from ddgs import DDGS  # type: ignore
        except Exception:
            return []

        results: list[KnowledgeItem] = []
        try:
            with DDGS() as ddgs:
                entries = ddgs.text(query, max_results=max_results)
                for index, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        continue
                    results.append(
                        KnowledgeItem(
                            source="web",
                            title=str(entry.get("title", "web-result")).strip(),
                            snippet=str(entry.get("body", "")).strip()[:220],
                            link=str(entry.get("href", "")).strip(),
                            score=float(max_results - index),
                        )
                    )
        except Exception:
            return []

        return results

    def _compose_enriched_requirement(
        self,
        requirement: str,
        local_items: list[KnowledgeItem],
        web_items: list[KnowledgeItem],
    ) -> str:
        notes: list[str] = []
        for item in local_items[:3]:
            notes.append(f"本地知识参考: {item.title} - {item.snippet}")
        for item in web_items[:3]:
            notes.append(f"外部最佳实践: {item.title} - {item.snippet}")

        if not notes:
            return requirement

        joined = "；".join(notes)
        return f"{requirement}。请结合以下上下文实现：{joined}"
