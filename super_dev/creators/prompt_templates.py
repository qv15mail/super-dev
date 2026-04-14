"""
Prompt 模板版本管理

开发：Excellent（11964948@qq.com）
功能：将 Prompt 模板从硬编码改为版本化文件，支持迭代优化
作用：提供 Prompt 模板的版本管理、渲染和历史追踪
创建时间：2026-03-28
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# 模板文件 front-matter 分隔符
_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class PromptTemplate:
    """版本化的 Prompt 模板。

    Attributes:
        id: 模板ID，如 ``prd-generator``.
        name: 人类可读的模板名称.
        version: 语义化版本号，如 ``1.0.0``.
        phase: 适用的流水线阶段，如 ``docs``, ``spec``, ``review``.
        description: 模板用途的简短描述.
        template: 模板内容，支持 ``{variable}`` 占位符.
        variables: 模板所需变量名称列表.
        metadata: 额外元数据（作者/创建时间/质量分/使用次数等）.
    """

    id: str
    name: str
    version: str
    phase: str
    description: str
    template: str
    variables: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def render(self, values: dict[str, str]) -> str:
        """用给定变量值渲染模板内容。

        Args:
            values: 变量名到值的映射.

        Returns:
            渲染后的字符串.

        Raises:
            KeyError: 缺少必需的变量.
        """
        missing = [v for v in self.variables if v not in values]
        if missing:
            raise KeyError(f"模板 '{self.id}' 缺少变量: {', '.join(missing)}")
        result = self.template
        for key, val in values.items():
            result = result.replace(f"{{{key}}}", str(val))
        return result


class PromptTemplateManager:
    """Prompt 模板管理器。

    从指定目录加载 Markdown 模板文件并提供查询、渲染、历史追踪等功能。
    模板文件使用 YAML front-matter 存储元数据，正文部分为模板内容。

    Args:
        templates_dir: 模板文件所在目录路径，默认为 ``super_dev/templates``.
    """

    def __init__(self, templates_dir: str = "super_dev/templates") -> None:
        self.templates_dir = self._resolve_templates_dir(templates_dir)
        self.templates: dict[str, PromptTemplate] = {}
        self._version_history: dict[str, list[dict]] = {}
        self._load_templates()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_template(self, template_id: str) -> PromptTemplate:
        """获取指定 ID 的模板。

        Args:
            template_id: 模板唯一标识符.

        Returns:
            匹配的 ``PromptTemplate`` 实例.

        Raises:
            KeyError: 未找到指定模板.
        """
        if template_id not in self.templates:
            raise KeyError(f"模板 '{template_id}' 不存在。可用模板: {list(self.templates.keys())}")
        return self.templates[template_id]

    def render(self, template_id: str, variables: dict[str, str]) -> str:
        """渲染指定模板。

        查找模板并用给定变量替换占位符，同时递增使用次数计数。

        Args:
            template_id: 模板唯一标识符.
            variables: 变量名到值的映射.

        Returns:
            渲染后的完整文本.
        """
        tpl = self.get_template(template_id)
        tpl.metadata["usage_count"] = tpl.metadata.get("usage_count", 0) + 1
        tpl.metadata["last_used"] = datetime.now().isoformat()
        return tpl.render(variables)

    def list_templates(self, phase: str | None = None) -> list[PromptTemplate]:
        """列出模板，可按阶段过滤。

        Args:
            phase: 如果提供，只返回属于该阶段的模板.

        Returns:
            匹配的模板列表.
        """
        templates = list(self.templates.values())
        if phase is not None:
            templates = [t for t in templates if t.phase == phase]
        return templates

    def get_template_history(self, template_id: str) -> list[dict]:
        """获取模板版本历史。

        Args:
            template_id: 模板唯一标识符.

        Returns:
            版本历史记录列表，每条包含 ``version``, ``date``, ``author``, ``description``.
        """
        return self._version_history.get(template_id, [])

    def register_template(self, template: PromptTemplate) -> None:
        """手动注册一个模板到管理器（不从文件加载）。

        Args:
            template: 要注册的 ``PromptTemplate`` 实例.
        """
        self.templates[template.id] = template
        self._record_version(template)
        logger.info("已注册模板: %s v%s", template.id, template.version)

    def reload(self) -> None:
        """重新从磁盘加载所有模板。"""
        self.templates.clear()
        self._version_history.clear()
        self._load_templates()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_templates(self) -> None:
        """扫描模板目录，加载所有 ``.md`` 模板文件。"""
        if not self.templates_dir.exists():
            logger.warning("模板目录不存在: %s", self.templates_dir)
            return

        for md_file in sorted(self.templates_dir.glob("*_template_*.md")):
            try:
                template = self._parse_template_file(md_file)
                if template:
                    self.templates[template.id] = template
                    self._record_version(template)
                    logger.debug("已加载模板: %s v%s (%s)", template.id, template.version, md_file.name)
            except Exception:
                logger.exception("加载模板文件失败: %s", md_file)

        # 同时尝试从 manifest.yaml 补充信息
        self._load_manifest()

        logger.debug("共加载 %d 个 Prompt 模板", len(self.templates))

    def _resolve_templates_dir(self, templates_dir: str) -> Path:
        candidate = Path(templates_dir)
        if candidate.is_absolute():
            return candidate

        cwd_candidate = Path.cwd() / candidate
        if cwd_candidate.exists():
            return cwd_candidate

        return Path(__file__).resolve().parent.parent / "templates"

    def _parse_template_file(self, path: Path) -> PromptTemplate | None:
        """解析单个 Markdown 模板文件。

        文件格式要求：以 ``---`` 包裹的 YAML front-matter，后跟模板正文。

        Args:
            path: 模板文件路径.

        Returns:
            解析出的 ``PromptTemplate``，如果格式不合法则返回 ``None``.
        """
        content = path.read_text(encoding="utf-8")
        match = _FRONT_MATTER_RE.match(content)
        if not match:
            logger.warning("模板文件缺少 front-matter: %s", path)
            return None

        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            logger.exception("解析 front-matter 失败: %s", path)
            return None

        template_body = content[match.end():]

        template_id: str = meta.get("id", path.stem)
        variables: list[str] = meta.get("variables", [])

        return PromptTemplate(
            id=template_id,
            name=meta.get("name", template_id),
            version=str(meta.get("version", "0.0.0")),
            phase=meta.get("phase", "unknown"),
            description=meta.get("description", ""),
            template=template_body,
            variables=variables,
            metadata={
                "author": meta.get("author", "unknown"),
                "quality_score": meta.get("quality_score", 0),
                "usage_count": meta.get("usage_count", 0),
                "created_at": meta.get("created_at", datetime.now().isoformat()),
                "source_file": str(path),
            },
        )

    def _load_manifest(self) -> None:
        """从 manifest.yaml 加载额外的模板元数据。"""
        manifest_path = self.templates_dir / "manifest.yaml"
        if not manifest_path.exists():
            return

        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            logger.exception("解析 manifest.yaml 失败")
            return

        for entry in data.get("templates", []):
            tid = entry.get("id")
            if tid and tid in self.templates:
                tpl = self.templates[tid]
                # 用 manifest 的描述 / 元数据覆盖（如果有）
                if "description" in entry:
                    tpl.description = entry["description"]
                if "name" in entry:
                    tpl.name = entry["name"]
                for k, v in entry.get("metadata", {}).items():
                    tpl.metadata[k] = v

    def _record_version(self, template: PromptTemplate) -> None:
        """向版本历史中追加一条记录。"""
        if template.id not in self._version_history:
            self._version_history[template.id] = []
        self._version_history[template.id].append(
            {
                "version": template.version,
                "date": datetime.now().isoformat(),
                "author": template.metadata.get("author", "unknown"),
                "description": template.description,
            }
        )
