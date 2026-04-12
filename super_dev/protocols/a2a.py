"""
A2A 协议基础支持

开发：Excellent（11964948@qq.com）
功能：让 Super Dev 的专家能力以 A2A Agent Card 的形式暴露
作用：支持外部 Agent 发现和调用 Super Dev 的治理能力
创建时间：2025-12-30

A2A 标准: https://github.com/a2aproject/A2A
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class A2AAgentCard:
    """A2A Agent Card — 描述一个可调用的 Agent 能力。

    符合 Google A2A (Agent-to-Agent) 协议规范，
    用于向外部系统暴露 Super Dev 的治理能力。
    """

    name: str
    description: str
    version: str
    capabilities: list[str] = field(default_factory=list)
    input_schema: dict = field(default_factory=dict)  # type: ignore[type-arg]
    output_schema: dict = field(default_factory=dict)  # type: ignore[type-arg]

    def to_dict(self) -> dict:  # type: ignore[type-arg]
        """导出为 A2A 兼容格式。"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema),
        }

    @classmethod
    def from_dict(cls, data: dict) -> A2AAgentCard:  # type: ignore[type-arg]
        """从字典构造 Agent Card。"""
        return cls(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            version=str(data.get("version", "")),
            capabilities=list(data.get("capabilities", [])),
            input_schema=dict(data.get("input_schema", {})),
            output_schema=dict(data.get("output_schema", {})),
        )


# ---------------------------------------------------------------------------
# 预定义的 input / output schema 常量
# ---------------------------------------------------------------------------

_PROJECT_DIR_INPUT = {
    "type": "object",
    "properties": {"project_dir": {"type": "string"}},
    "required": ["project_dir"],
}

_SCORE_PASSED_OUTPUT = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "passed": {"type": "boolean"},
    },
    "required": ["score", "passed"],
}

_ISSUES_OUTPUT = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string"},
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
        },
    },
    "required": ["issues"],
}

_SPEC_INPUT = {
    "type": "object",
    "properties": {
        "change_id": {"type": "string"},
        "project_dir": {"type": "string"},
    },
    "required": ["change_id"],
}

_VALIDATION_OUTPUT = {
    "type": "object",
    "properties": {
        "valid": {"type": "boolean"},
        "errors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["valid", "errors"],
}

_QUERY_INPUT = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "domain": {"type": "string"},
    },
    "required": ["query"],
}

_ADVICE_OUTPUT = {
    "type": "object",
    "properties": {
        "domain": {"type": "string"},
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "references": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["recommendations"],
}

_VERSION = "2.3.6"


class SuperDevA2AProvider:
    """Super Dev A2A 能力提供者。

    将 Super Dev 的核心治理能力注册为 A2A Agent Card，
    以便外部 Agent 通过标准协议发现和调用。
    """

    def __init__(self) -> None:
        self._agents: dict[str, A2AAgentCard] = self._register_agents()

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def list_agents(self) -> list[A2AAgentCard]:
        """列出所有可用 Agent。"""
        return list(self._agents.values())

    def get_agent(self, name: str) -> A2AAgentCard | None:
        """获取指定 Agent，不存在时返回 ``None``。"""
        return self._agents.get(name)

    def generate_agent_cards_json(self) -> str:
        """生成 A2A Agent Cards JSON（可放在 ``.well-known/a2a.json``）。"""
        payload = {
            "provider": "super-dev",
            "version": _VERSION,
            "agents": [card.to_dict() for card in self._agents.values()],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 内部注册
    # ------------------------------------------------------------------

    def _register_agents(self) -> dict[str, A2AAgentCard]:
        """注册 Super Dev 的治理能力为 A2A Agent。"""
        return {
            "quality-gate": A2AAgentCard(
                name="super-dev-quality-gate",
                description="AI 代码质量门禁检查，覆盖安全/性能/文档/测试/架构",
                version=_VERSION,
                capabilities=["quality_check", "security_scan", "validation_rules"],
                input_schema=_PROJECT_DIR_INPUT,
                output_schema=_SCORE_PASSED_OUTPUT,
            ),
            "redteam": A2AAgentCard(
                name="super-dev-redteam",
                description="红队审查：安全/性能/架构的对抗式审查",
                version=_VERSION,
                capabilities=["security_audit", "performance_review", "architecture_review"],
                input_schema=_PROJECT_DIR_INPUT,
                output_schema=_ISSUES_OUTPUT,
            ),
            "spec-validator": A2AAgentCard(
                name="super-dev-spec-validator",
                description="Spec 提案校验：检查变更提案格式与完整性",
                version=_VERSION,
                capabilities=["spec_validation", "format_check", "completeness_check"],
                input_schema=_SPEC_INPUT,
                output_schema=_VALIDATION_OUTPUT,
            ),
            "knowledge-advisor": A2AAgentCard(
                name="super-dev-knowledge-advisor",
                description="知识库顾问：基于 21 个领域知识库提供标准与最佳实践建议",
                version=_VERSION,
                capabilities=["knowledge_lookup", "best_practice", "standard_reference"],
                input_schema=_QUERY_INPUT,
                output_schema=_ADVICE_OUTPUT,
            ),
            "quality-advisor": A2AAgentCard(
                name="super-dev-quality-advisor",
                description="质量顾问：提供代码质量改进建议与技术债务评估",
                version=_VERSION,
                capabilities=["code_review", "tech_debt_assessment", "improvement_plan"],
                input_schema=_PROJECT_DIR_INPUT,
                output_schema=_ADVICE_OUTPUT,
            ),
        }
