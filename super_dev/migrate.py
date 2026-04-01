"""版本迁移工具。"""

from __future__ import annotations

from pathlib import Path

import yaml


def migrate_project(project_dir: Path) -> list[str]:
    """将 2.2.0 项目迁移到 2.3.0。

    返回变更描述列表。
    """
    changes: list[str] = []

    # 1. 更新 super-dev.yaml 版本号
    config_path = project_dir / "super-dev.yaml"
    if config_path.exists():
        try:
            text = config_path.read_text(encoding="utf-8")
            data = yaml.safe_load(text) or {}
            old_version = data.get("version", "")
            if old_version != "2.3.0":
                data["version"] = "2.3.0"
                config_path.write_text(
                    yaml.dump(data, allow_unicode=True, default_flow_style=False),
                    encoding="utf-8",
                )
                changes.append(f"super-dev.yaml 版本号 {old_version} -> 2.3.0")
        except Exception as exc:
            changes.append(f"super-dev.yaml 更新失败: {exc}")

    # 2. 重新生成 .claude/CLAUDE.md（如果存在）
    claude_md = project_dir / ".claude" / "CLAUDE.md"
    if claude_md.exists():
        try:
            from .integrations.manager import IntegrationManager

            mgr = IntegrationManager(project_dir=project_dir)
            written = mgr.setup(target="claude-code", force=True)
            if written:
                changes.append("已重新生成 .claude/CLAUDE.md（含 2.3.0 编码约束）")
        except Exception as exc:
            changes.append(f".claude/CLAUDE.md 重新生成失败: {exc}")

    # 3. 重新生成 SKILL.md（如果存在）
    skill_candidates = (
        list((project_dir / ".claude").rglob("SKILL.md"))
        if (project_dir / ".claude").exists()
        else []
    )
    if skill_candidates:
        try:
            from .skills.manager import SkillManager

            sm = SkillManager(project_dir=project_dir)
            sm.install(source="super-dev", target="claude-code", force=True)
            changes.append("已重新生成 SKILL.md（含 2.3.0 内容）")
        except Exception as exc:
            changes.append(f"SKILL.md 重新生成失败: {exc}")

    # 4. 创建 .super-dev/memory/ 目录
    memory_dir = project_dir / ".super-dev" / "memory"
    if not memory_dir.exists():
        memory_dir.mkdir(parents=True, exist_ok=True)
        changes.append("已创建 .super-dev/memory/ 目录")

    # 5. 安装 enforcement hooks
    try:
        from .enforcement import HostHooksConfigurator

        configurator = HostHooksConfigurator(project_dir)
        settings_path = configurator.install_hooks(host="claude-code")
        if settings_path.exists():
            changes.append("已安装 enforcement hooks")
    except Exception:
        pass  # enforcement 是可选的

    return changes
