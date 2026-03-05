"""
知识增强模块

将用户输入需求通过「本地知识库 + 联网检索」进行增强，
为后续 PRD / 架构 / UIUX / Spec 生成提供更完整上下文。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests  # type: ignore[import-untyped]


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

    def __init__(
        self,
        project_dir: Path,
        web_enabled: bool = True,
        allowed_web_domains: list[str] | None = None,
        cache_ttl_seconds: int | None = None,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.web_enabled = web_enabled
        self.docs_dir = self.project_dir / "docs"
        self.specs_dir = self.project_dir / ".super-dev" / "specs"
        self.data_dir = self.project_dir / "super_dev" / "data"
        self.builtin_data_dir = Path(__file__).resolve().parents[1] / "data"
        env_domains = [
            item.strip().lower()
            for item in os.getenv("SUPER_DEV_KNOWLEDGE_ALLOWED_DOMAINS", "").split(",")
            if item.strip()
        ]
        selected_domains = allowed_web_domains if allowed_web_domains is not None else env_domains
        self.allowed_web_domains = [item.strip().lower() for item in selected_domains if item.strip()]
        env_cache_ttl = os.getenv("SUPER_DEV_KNOWLEDGE_CACHE_TTL_SECONDS", "").strip()
        env_cache_ttl_value = int(env_cache_ttl) if env_cache_ttl.isdigit() else 1800
        self.cache_ttl_seconds = cache_ttl_seconds if cache_ttl_seconds is not None else env_cache_ttl_value
        self._last_web_stats: dict[str, Any] = {
            "provider": "none",
            "raw_count": 0,
            "filtered_count": 0,
            "filtered_out_count": 0,
        }

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
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "original_requirement": requirement,
            "domain": domain,
            "keywords": keywords,
            "local_knowledge": [item.to_dict() for item in local_items],
            "web_knowledge": [item.to_dict() for item in web_items],
            "citations": {
                "local": [self._to_citation(item) for item in local_items],
                "web": [self._to_citation(item) for item in web_items],
            },
            "metadata": {
                "web_enabled": self.web_enabled,
                "allowed_web_domains": self.allowed_web_domains,
                "web_stats": self._last_web_stats,
            },
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

    def save_bundle(
        self,
        bundle: dict[str, Any],
        output_dir: Path,
        project_name: str,
        requirement: str | None = None,
        domain: str | None = None,
    ) -> Path:
        cache_dir = Path(output_dir) / "knowledge-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{project_name}-knowledge-bundle.json"
        cached_bundle = dict(bundle)
        cached_bundle.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
        if requirement is not None:
            cached_bundle["cache_signature"] = self._bundle_signature(
                requirement=requirement,
                domain=domain or "",
            )
        cached_bundle["cache_ttl_seconds"] = self.cache_ttl_seconds
        cache_file.write_text(json.dumps(cached_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        return cache_file

    def load_cached_bundle(
        self,
        output_dir: Path,
        project_name: str,
        requirement: str,
        domain: str = "",
    ) -> dict[str, Any] | None:
        if self.cache_ttl_seconds <= 0:
            return None

        cache_file = Path(output_dir) / "knowledge-cache" / f"{project_name}-knowledge-bundle.json"
        if not cache_file.exists():
            return None
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None

        generated_at_raw = str(payload.get("generated_at", "")).strip()
        cache_signature = str(payload.get("cache_signature", "")).strip()
        if not generated_at_raw or not cache_signature:
            return None

        expected_signature = self._bundle_signature(requirement=requirement, domain=domain)
        if cache_signature != expected_signature:
            return None

        generated_at = self._parse_datetime(generated_at_raw)
        if generated_at is None:
            return None
        expired_at = generated_at + timedelta(seconds=self.cache_ttl_seconds)
        if expired_at <= datetime.now(timezone.utc):
            return None
        return payload

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
            content = ""
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""
            if not content:
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

    def _to_citation(self, item: KnowledgeItem) -> dict[str, str]:
        return {
            "title": item.title,
            "source": item.source,
            "link": item.link,
        }

    def _build_web_query(self, requirement: str, domain: str) -> str:
        if domain:
            return f"{requirement} {domain} best practices architecture ui ux"
        return f"{requirement} best practices architecture ui ux"

    def _collect_web_items(self, query: str, max_results: int) -> list[KnowledgeItem]:
        if not self.web_enabled:
            self._last_web_stats = {
                "provider": "disabled",
                "raw_count": 0,
                "filtered_count": 0,
                "filtered_out_count": 0,
            }
            return []

        provider = "ddgs"
        results = self._collect_web_items_ddgs(query=query, max_results=max_results)
        if not results:
            provider = "duckduckgo"
            results = self._collect_web_items_duckduckgo(query=query, max_results=max_results)
        raw_count = len(results)
        filtered = self._filter_web_items(results)[:max_results]
        self._last_web_stats = {
            "provider": provider,
            "raw_count": raw_count,
            "filtered_count": len(filtered),
            "filtered_out_count": max(raw_count - len(filtered), 0),
        }
        return filtered

    def _filter_web_items(self, items: list[KnowledgeItem]) -> list[KnowledgeItem]:
        if not self.allowed_web_domains:
            return items

        filtered: list[KnowledgeItem] = []
        for item in items:
            if not item.link:
                continue
            parsed = urllib.parse.urlparse(item.link)
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            if any(netloc == domain or netloc.endswith(f".{domain}") for domain in self.allowed_web_domains):
                filtered.append(item)
        return filtered

    def _collect_web_items_ddgs(self, query: str, max_results: int) -> list[KnowledgeItem]:
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

    def _collect_web_items_duckduckgo(self, query: str, max_results: int) -> list[KnowledgeItem]:
        encoded_query = urllib.parse.quote(query)
        url = (
            "https://api.duckduckgo.com/"
            f"?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        )

        try:
            response = requests.get(url, timeout=6)
            if response.status_code >= 400:
                return []
            payload = response.text
            data = json.loads(payload)
        except Exception:
            return []

        results: list[KnowledgeItem] = []
        abstract = str(data.get("Abstract", "")).strip()
        if abstract:
            results.append(
                KnowledgeItem(
                    source="web",
                    title=str(data.get("Heading", "DuckDuckGo Result")).strip() or "DuckDuckGo Result",
                    snippet=abstract[:220],
                    link=str(data.get("AbstractURL", "")).strip(),
                    score=float(max_results),
                )
            )

        related = data.get("RelatedTopics", [])
        for item in related:
            if len(results) >= max_results:
                break
            if not isinstance(item, dict):
                continue
            if "Topics" in item and isinstance(item.get("Topics"), list):
                sub_topics = item.get("Topics", [])
            else:
                sub_topics = [item]

            for topic in sub_topics:
                if len(results) >= max_results:
                    break
                if not isinstance(topic, dict):
                    continue
                text = str(topic.get("Text", "")).strip()
                if not text:
                    continue
                results.append(
                    KnowledgeItem(
                        source="web",
                        title=text[:80],
                        snippet=text[:220],
                        link=str(topic.get("FirstURL", "")).strip(),
                        score=float(max_results - len(results)),
                    )
                )

        return results[:max_results]

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

    def _bundle_signature(self, requirement: str, domain: str) -> str:
        normalized_requirement = requirement.strip().lower()
        normalized_domain = domain.strip().lower()
        allowed_domains = ",".join(sorted(self.allowed_web_domains))
        payload = f"{normalized_requirement}|{normalized_domain}|{self.web_enabled}|{allowed_domains}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _parse_datetime(self, value: str) -> datetime | None:
        cleaned = value.strip()
        if not cleaned:
            return None
        normalized = cleaned.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
