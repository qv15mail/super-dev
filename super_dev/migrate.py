"""版本迁移工具。"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from . import __version__


def _detect_onboarded_hosts(project_dir: Path) -> list[str]:
    """检测项目中已经接入过的宿主。"""
    from .integrations.manager import IntegrationManager

    mgr = IntegrationManager(project_dir=project_dir)
    detected: list[str] = []
    for target_name, target_obj in mgr.TARGETS.items():
        for rel in target_obj.files:
            if rel in target_obj.optional_files:
                continue
            full = project_dir / rel
            if full.exists():
                detected.append(target_name)
                break
    return detected


def _cleanup_claude_code_legacy(project_dir: Path, changes: list[str]) -> None:
    """清理 Claude Code 旧版 super-dev-core 残留。"""
    legacy_paths = [
        Path.home() / ".claude" / "skills" / "super-dev-core",
        Path.home() / ".claude" / "agents" / "super-dev-core.md",
        project_dir / ".claude" / "agents" / "super-dev-core.md",
    ]
    for legacy in legacy_paths:
        if legacy.exists():
            try:
                if legacy.is_dir():
                    shutil.rmtree(legacy)
                else:
                    legacy.unlink()
                changes.append(f"已清理旧版残留: {legacy.name}")
            except Exception:
                pass


def migrate_project(project_dir: Path) -> list[str]:
    """将旧版项目迁移到当前版本。

    自动检测已接入的宿主，重新生成所有配置文件和 Skill。
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
            if old_version != __version__:
                data["version"] = __version__
                config_path.write_text(
                    yaml.dump(data, allow_unicode=True, default_flow_style=False),
                    encoding="utf-8",
                )
                changes.append(f"super-dev.yaml 版本号 {old_version} -> {__version__}")
        except Exception as exc:
            changes.append(f"super-dev.yaml 更新失败: {exc}")

    # 2. 检测所有已接入宿主并重新生成配置
    detected_hosts = _detect_onboarded_hosts(project_dir)

    if detected_hosts:
        from .integrations.manager import IntegrationManager
        from .skills.manager import SkillManager

        mgr = IntegrationManager(project_dir=project_dir)
        sm = SkillManager(project_dir=project_dir)

        for target in detected_hosts:
            try:
                written = mgr.setup(target=target, force=True)
                if written:
                    changes.append(f"已重新生成 {target} 集成配置")
            except Exception as exc:
                changes.append(f"{target} 集成配置更新失败: {exc}")

            # 重新生成 slash command
            try:
                if mgr.supports_slash(target):
                    mgr.setup_slash_command(target=target, force=True)
                    mgr.setup_global_slash_command(target=target, force=True)
            except Exception:
                pass

            # 重新生成全局协议
            try:
                mgr.setup_global_protocol(target=target, force=True)
            except Exception:
                pass

            # 重新安装 Skill
            if mgr.requires_skill(target):
                try:
                    if sm.skill_surface_available(target):
                        skill_name = sm.default_skill_name(target)
                        sm.install(
                            source="super-dev",
                            target=target,
                            name=skill_name,
                            force=True,
                        )
                        changes.append(f"已更新 {target} Skill ({skill_name})")
                except Exception as exc:
                    changes.append(f"{target} Skill 更新失败: {exc}")

        # Claude Code 特有清理
        if "claude-code" in detected_hosts:
            _cleanup_claude_code_legacy(project_dir, changes)

    # 3. 创建 .super-dev/memory/ 目录
    memory_dir = project_dir / ".super-dev" / "memory"
    if not memory_dir.exists():
        memory_dir.mkdir(parents=True, exist_ok=True)
        changes.append("已创建 .super-dev/memory/ 目录")

    # 4. 安装 enforcement hooks
    try:
        from .enforcement import HostHooksConfigurator

        configurator = HostHooksConfigurator(project_dir)
        settings_path = configurator.install_hooks(host="claude-code")
        if settings_path.exists():
            changes.append("已安装 enforcement hooks")
    except Exception:
        pass  # enforcement 是可选的

    if not changes:
        changes.append("项目已是最新版本，无需迁移")

    return changes
