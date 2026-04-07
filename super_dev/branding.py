"""统一终端输出格式与阶段标识。"""

from __future__ import annotations

LOGO_COMPACT = "Super Dev"
VERSION = "2.3.3"

# 阶段编号和名称映射
PHASE_NAMES: dict[str, str] = {
    "research": "研究调研",
    "prd": "需求文档",
    "architecture": "架构设计",
    "uiux": "UI/UX 设计",
    "spec": "Spec 拆解",
    "frontend": "前端开发",
    "backend": "后端开发",
    "quality": "质量门禁",
    "delivery": "交付打包",
}

PHASE_NUMBERS: dict[str, int] = {
    "research": 1,
    "prd": 2,
    "architecture": 3,
    "uiux": 4,
    "spec": 5,
    "frontend": 6,
    "backend": 7,
    "quality": 8,
    "delivery": 9,
}

PHASE_EXPERTS: dict[str, str] = {
    "research": "PM + ARCHITECT",
    "prd": "PM",
    "architecture": "ARCHITECT + DBA",
    "uiux": "UI + UX",
    "spec": "PM + CODE",
    "frontend": "CODE + UI",
    "backend": "CODE + DBA",
    "quality": "QA + SECURITY",
    "delivery": "DEVOPS + QA",
}


def banner(title: str = "", phase: str = "") -> str:
    """生成品牌横幅，宿主终端和用户都能看到。"""
    lines = []
    lines.append(f"{'=' * 60}")
    if phase:
        num = PHASE_NUMBERS.get(phase, "?")
        name = PHASE_NAMES.get(phase, phase)
        expert = PHASE_EXPERTS.get(phase, "")
        lines.append(f"  {LOGO_COMPACT} v{VERSION} | Phase {num}/9: {name}")
        if expert:
            lines.append(f"  Expert: {expert}")
    elif title:
        lines.append(f"  {LOGO_COMPACT} v{VERSION} | {title}")
    else:
        lines.append(f"  {LOGO_COMPACT} v{VERSION}")
    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


def phase_start(phase: str) -> str:
    """阶段开始标识。"""
    num = PHASE_NUMBERS.get(phase, "?")
    name = PHASE_NAMES.get(phase, phase)
    expert = PHASE_EXPERTS.get(phase, "")
    lines = [
        "",
        f"{'─' * 50}",
        f"  {LOGO_COMPACT} | [{num}/9] {name} 开始",
    ]
    if expert:
        lines.append(f"  主导专家: {expert}")
    lines.append(f"{'─' * 50}")
    return "\n".join(lines)


def phase_complete(phase: str, success: bool = True, score: float = 0.0) -> str:
    """阶段完成标识。"""
    num = PHASE_NUMBERS.get(phase, "?")
    name = PHASE_NAMES.get(phase, phase)
    status = "完成" if success else "失败"
    icon = "[OK]" if success else "[FAIL]"
    line = f"  {LOGO_COMPACT} | [{num}/9] {name} {status}"
    if score > 0:
        line += f" (质量: {score:.1f}分)"
    return f"\n{icon} {line}"


def gate_check(gate_name: str, passed: bool) -> str:
    """门禁检查结果。"""
    icon = "[OK]" if passed else "[FAIL]"
    status = "通过" if passed else "未通过"
    return f"  {icon} {LOGO_COMPACT} 门禁 | {gate_name}: {status}"


def enforcement_notice(rule: str) -> str:
    """执行约束提醒（在宿主终端显示）。"""
    return f"  {LOGO_COMPACT} 约束 | {rule}"


def command_header(command: str) -> str:
    """CLI 命令的品牌头部。"""
    return f"\n{LOGO_COMPACT} v{VERSION} > {command}\n"


def progress_bar(current: int, total: int, label: str = "") -> str:
    """简单的文本进度条。"""
    width = 30
    filled = int(width * current / max(total, 1))
    bar = "#" * filled + "-" * (width - filled)
    pct = int(100 * current / max(total, 1))
    text = f"  [{bar}] {pct}% ({current}/{total})"
    if label:
        text += f" {label}"
    return text


# 宿主应该在聊天中显示的阶段宣告模板
PHASE_ANNOUNCEMENT_TEMPLATE = """
**{logo} Pipeline | Phase {num}/9: {name}**
主导专家: {expert}
{description}
"""


def host_phase_announcement(phase: str, description: str = "") -> str:
    """生成宿主应该在聊天中显示的阶段宣告。

    这个文本写入 SKILL.md，宿主在进入每个阶段时应该打印。
    """
    return PHASE_ANNOUNCEMENT_TEMPLATE.format(
        logo=LOGO_COMPACT,
        num=PHASE_NUMBERS.get(phase, "?"),
        name=PHASE_NAMES.get(phase, phase),
        expert=PHASE_EXPERTS.get(phase, ""),
        description=description,
    ).strip()
