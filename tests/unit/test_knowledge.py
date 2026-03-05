"""
知识增强器测试
"""

from pathlib import Path

from super_dev.orchestrator.knowledge import KnowledgeAugmenter, KnowledgeItem


class TestKnowledgeAugmenter:
    def test_augment_with_local_knowledge(self, temp_project_dir: Path):
        docs_dir = temp_project_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "auth.md").write_text(
            "# 认证设计\n\n登录功能必须支持 token 刷新与权限控制。",
            encoding="utf-8",
        )

        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=False)
        bundle = augmenter.augment("实现登录认证流程", domain="auth")

        assert bundle["original_requirement"] == "实现登录认证流程"
        assert "generated_at" in bundle
        assert "citations" in bundle
        assert "metadata" in bundle
        assert "web_stats" in bundle["metadata"]
        assert len(bundle["local_knowledge"]) >= 1
        assert "请结合以下上下文实现" in bundle["enriched_requirement"]
        assert len(bundle["citations"]["local"]) >= 1

    def test_render_markdown(self, temp_project_dir: Path):
        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=False)
        bundle = {
            "original_requirement": "构建管理后台",
            "domain": "general",
            "keywords": ["管理", "后台"],
            "local_knowledge": [],
            "web_knowledge": [],
            "enriched_requirement": "构建管理后台。",
        }
        markdown = augmenter.to_markdown(bundle)
        assert "# 需求增强报告" in markdown
        assert "## 提取关键词" in markdown

    def test_web_fallback_when_ddgs_unavailable(self, temp_project_dir: Path, monkeypatch):
        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=True)

        monkeypatch.setattr(
            augmenter,
            "_collect_web_items_ddgs",
            lambda query, max_results: [],
        )
        monkeypatch.setattr(
            augmenter,
            "_collect_web_items_duckduckgo",
            lambda query, max_results: [
                KnowledgeItem(
                    source="web",
                    title="Fallback Result",
                    snippet="DuckDuckGo fallback snippet",
                    link="https://example.com",
                    score=1.0,
                )
            ],
        )

        bundle = augmenter.augment("实现登录认证流程", domain="auth")

        assert len(bundle["web_knowledge"]) == 1
        assert "Fallback Result" in bundle["enriched_requirement"]

    def test_web_prefers_ddgs_result(self, temp_project_dir: Path, monkeypatch):
        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=True)
        fallback_called = {"value": False}

        monkeypatch.setattr(
            augmenter,
            "_collect_web_items_ddgs",
            lambda query, max_results: [
                KnowledgeItem(
                    source="web",
                    title="DDGS Result",
                    snippet="Primary web snippet",
                    score=2.0,
                )
            ],
        )

        def _fallback(query: str, max_results: int) -> list[KnowledgeItem]:
            fallback_called["value"] = True
            return []

        monkeypatch.setattr(augmenter, "_collect_web_items_duckduckgo", _fallback)

        bundle = augmenter.augment("实现登录认证流程", domain="auth")

        assert len(bundle["web_knowledge"]) == 1
        assert bundle["web_knowledge"][0]["title"] == "DDGS Result"
        assert fallback_called["value"] is False

    def test_save_bundle_cache_file(self, temp_project_dir: Path):
        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=False)
        bundle = augmenter.augment("实现登录认证流程", domain="auth")
        output_dir = temp_project_dir / "output"
        cache_file = augmenter.save_bundle(
            bundle=bundle,
            output_dir=output_dir,
            project_name="demo",
            requirement="实现登录认证流程",
            domain="auth",
        )
        assert cache_file.exists()
        content = cache_file.read_text(encoding="utf-8")
        assert '"original_requirement": "实现登录认证流程"' in content
        assert '"cache_signature"' in content

    def test_load_cached_bundle_hit(self, temp_project_dir: Path):
        augmenter = KnowledgeAugmenter(project_dir=temp_project_dir, web_enabled=False, cache_ttl_seconds=1800)
        bundle = augmenter.augment("实现登录认证流程", domain="auth")
        output_dir = temp_project_dir / "output"
        augmenter.save_bundle(
            bundle=bundle,
            output_dir=output_dir,
            project_name="demo",
            requirement="实现登录认证流程",
            domain="auth",
        )

        cached = augmenter.load_cached_bundle(
            output_dir=output_dir,
            project_name="demo",
            requirement="实现登录认证流程",
            domain="auth",
        )
        assert cached is not None
        assert cached.get("original_requirement") == "实现登录认证流程"

    def test_web_items_filtered_by_allowed_domains(self, temp_project_dir: Path, monkeypatch):
        augmenter = KnowledgeAugmenter(
            project_dir=temp_project_dir,
            web_enabled=True,
            allowed_web_domains=["openai.com"],
        )

        monkeypatch.setattr(
            augmenter,
            "_collect_web_items_ddgs",
            lambda query, max_results: [
                KnowledgeItem(
                    source="web",
                    title="OpenAI API",
                    snippet="official docs",
                    link="https://platform.openai.com/docs/overview",
                    score=3.0,
                ),
                KnowledgeItem(
                    source="web",
                    title="Random Blog",
                    snippet="community post",
                    link="https://example.org/blog",
                    score=2.0,
                ),
            ],
        )
        monkeypatch.setattr(
            augmenter,
            "_collect_web_items_duckduckgo",
            lambda query, max_results: [],
        )

        bundle = augmenter.augment("如何实现 agent orchestration", domain="ai")
        web_items = bundle.get("web_knowledge", [])
        web_stats = (bundle.get("metadata") or {}).get("web_stats", {})

        assert len(web_items) == 1
        assert web_items[0]["title"] == "OpenAI API"
        assert web_stats.get("filtered_out_count") == 1
