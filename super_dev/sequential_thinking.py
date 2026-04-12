"""
Sequential Thinking Engine — 顺位思考引擎

参考 MCP Sequential Thinking Server 的设计，
为 Super Dev 流水线提供结构化的逐步推理能力。

核心特性：
- 编号思考步骤，每步建立在前一步之上
- 支持修正（revision）：发现前面想错了可以回溯修正
- 支持分支（branch）：遇到多个方向可以探索替代路径
- 动态调整：总步数可以随理解深入而增减
- 假设生成与验证：形成假设 → 验证 → 修正循环
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ThoughtStep:
    """一个思考步骤"""

    thought: str
    step_number: int
    total_steps: int
    next_needed: bool = True
    is_revision: bool = False
    revises_step: int | None = None
    branch_from: int | None = None
    branch_id: str | None = None
    needs_more: bool = False
    step_type: str = "analysis"  # analysis | revision | branch | hypothesis | verification | conclusion

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ThinkingSession:
    """一次完整的思考会话"""

    topic: str
    mode: str  # requirement | research | architecture | debug | competition
    steps: list[ThoughtStep] = field(default_factory=list)
    branches: dict[str, list[ThoughtStep]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    conclusion: str = ""

    @property
    def current_step(self) -> int:
        return len(self.steps)

    @property
    def branch_ids(self) -> list[str]:
        return list(self.branches.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "mode": self.mode,
            "total_steps": len(self.steps),
            "branches": self.branch_ids,
            "conclusion": self.conclusion,
            "steps": [step.to_dict() for step in self.steps],
        }


class SequentialThinkingEngine:
    """顺位思考引擎"""

    def __init__(self) -> None:
        self.sessions: list[ThinkingSession] = []
        self._current: ThinkingSession | None = None

    def start(self, topic: str, mode: str = "requirement", estimated_steps: int = 7) -> ThinkingSession:
        """开始一个新的思考会话"""
        session = ThinkingSession(topic=topic, mode=mode)
        self.sessions.append(session)
        self._current = session
        return session

    def think(
        self,
        thought: str,
        *,
        step_type: str = "analysis",
        is_revision: bool = False,
        revises_step: int | None = None,
        branch_from: int | None = None,
        branch_id: str | None = None,
        needs_more: bool = False,
        next_needed: bool = True,
    ) -> ThoughtStep:
        """记录一个思考步骤"""
        if self._current is None:
            raise RuntimeError("No active thinking session. Call start() first.")

        step_number = self._current.current_step + 1
        total_steps = max(step_number, len(self._current.steps) + 1)

        if needs_more:
            total_steps += 2

        step = ThoughtStep(
            thought=thought,
            step_number=step_number,
            total_steps=total_steps,
            next_needed=next_needed,
            is_revision=is_revision,
            revises_step=revises_step,
            branch_from=branch_from,
            branch_id=branch_id,
            needs_more=needs_more,
            step_type=step_type,
        )

        self._current.steps.append(step)

        if branch_from and branch_id:
            if branch_id not in self._current.branches:
                self._current.branches[branch_id] = []
            self._current.branches[branch_id].append(step)

        return step

    def revise(self, step_number: int, new_thought: str) -> ThoughtStep:
        """修正一个前序步骤的结论"""
        return self.think(
            new_thought,
            step_type="revision",
            is_revision=True,
            revises_step=step_number,
        )

    def branch(self, from_step: int, branch_id: str, thought: str) -> ThoughtStep:
        """从某个步骤分支出替代路径"""
        return self.think(
            thought,
            step_type="branch",
            branch_from=from_step,
            branch_id=branch_id,
        )

    def hypothesize(self, hypothesis: str) -> ThoughtStep:
        """生成假设"""
        return self.think(hypothesis, step_type="hypothesis")

    def verify(self, verification: str, *, valid: bool = True) -> ThoughtStep:
        """验证假设"""
        prefix = "✓ 验证通过" if valid else "✗ 验证失败"
        return self.think(f"{prefix}：{verification}", step_type="verification")

    def conclude(self, conclusion: str) -> ThoughtStep:
        """得出结论"""
        if self._current:
            self._current.conclusion = conclusion
        return self.think(conclusion, step_type="conclusion", next_needed=False)

    def format_step(self, step: ThoughtStep) -> str:
        """格式化一个思考步骤为可读文本"""
        type_labels = {
            "analysis": "💭 分析",
            "revision": "🔄 修正",
            "branch": "🌿 分支",
            "hypothesis": "💡 假设",
            "verification": "✅ 验证",
            "conclusion": "🎯 结论",
        }
        label = type_labels.get(step.step_type, "💭 思考")

        context = ""
        if step.is_revision and step.revises_step:
            context = f"（修正 Step {step.revises_step}）"
        elif step.branch_from and step.branch_id:
            context = f"（从 Step {step.branch_from} 分支，ID: {step.branch_id}）"

        header = f"{label} Step {step.step_number}/{step.total_steps}{context}"
        return f"{header}\n{step.thought}"

    def format_session(self, session: ThinkingSession | None = None) -> str:
        """格式化完整的思考会话"""
        session = session or self._current
        if not session:
            return ""

        lines = [f"[顺位思考] {session.topic}", f"模式: {session.mode}", ""]
        for step in session.steps:
            lines.append(self.format_step(step))
            lines.append("")

        if session.conclusion:
            lines.append(f"结论: {session.conclusion}")

        return "\n".join(lines)

    def save(self, output_dir: Path, filename: str = "thinking.json") -> Path:
        """保存思考会话到文件"""
        if not self._current:
            raise RuntimeError("No active session to save.")

        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        filepath.write_text(
            json.dumps(self._current.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return filepath


# ============================================================
# 预设思考模板 — 不同场景的思考步骤定义
# ============================================================

REQUIREMENT_THINKING_STEPS = {
    "standard": [
        {"step": 1, "label": "理解需求本质", "prompt": "这是什么类型的产品？解决什么问题？服务谁？"},
        {"step": 2, "label": "识别核心价值", "prompt": "用户为什么要用这个？核心价值主张是什么？和现有方案的差异在哪？"},
        {"step": 3, "label": "拆解功能域", "prompt": "按用户旅程拆分功能模块。用户从打开到完成目标要经过哪些步骤？"},
        {"step": 4, "label": "判断技术方向", "prompt": "前端框架？后端架构？数据存储？部署方式？为什么选这些？"},
        {"step": 5, "label": "识别风险与约束", "prompt": "技术风险、时间约束、业务规则、安全要求、性能预期？"},
        {"step": 6, "label": "确定优先级", "prompt": "哪些是 MVP 必须的？哪些可以后续迭代？按什么标准排优先级？"},
        {"step": 7, "label": "回顾修正", "prompt": "前面的步骤有矛盾吗？优先级合理吗？漏掉了什么？"},
    ],
    "competition": [
        {"step": 1, "label": "理解本质", "prompt": "这个东西本质是什么？一句话定义它。"},
        {"step": 2, "label": "核心体验", "prompt": "用户打开后最先感受到什么？不是功能列表，是感受。"},
        {"step": 3, "label": "演示路径", "prompt": "从打开到'哇'的最短路径是什么？打开→看到X→点击Y→发生Z→'哇'"},
        {"step": 4, "label": "锁定 P0", "prompt": "从演示路径中提取 ≤3 个必须完成的功能。砍掉哪个路径还能走通就砍。"},
        {"step": 5, "label": "识别 P1", "prompt": "什么能让作品从'能用'变成'惊艳'？一个动效？一个细节？一个交互？"},
        {"step": 6, "label": "声明不做", "prompt": "明确放弃什么。用户注册？设置页面？数据持久化？响应式？"},
        {"step": 7, "label": "回顾修正", "prompt": "P0 是不是太多？演示路径走得通吗？有没有前后矛盾？"},
    ],
}


def create_engine() -> SequentialThinkingEngine:
    """创建一个新的顺位思考引擎实例"""
    return SequentialThinkingEngine()
