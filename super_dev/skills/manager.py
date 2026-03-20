"""
Skill 安装管理器
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..catalogs import HOST_TOOL_IDS


@dataclass
class SkillInstallResult:
    name: str
    target: str
    path: Path
    source: str


class SkillManager:
    """跨平台 AI Coding 工具 Skill 管理"""

    # Official user-level skill paths confirmed by vendor docs.
    OFFICIAL_TARGET_PATHS = {
        "antigravity": "~/.gemini/skills",
        "codebuddy-cli": "~/.codebuddy/skills",
        "codebuddy": "~/.codebuddy/skills",
        "codex-cli": "~/.codex/skills",
        "iflow": "~/.iflow/skills",
        "jetbrains-ai": "~/.junie/skills",
        "opencode": "~/.config/opencode/skills",
        "qoder-cli": "~/.qoder/skills",
        "qoder": "~/.qoderwork/skills",
        "roo-code": "~/.roo/skills",
        "windsurf": "~/.codeium/windsurf/skills",
    }

    # Observed compatibility paths used when a host exposes a local skill loader
    # but the vendor docs do not yet publish a stable user-level install path.
    OBSERVED_TARGET_PATHS = {
        "aider": "~/.aider/skills",
        "claude-code": "~/.claude/skills",
        "cline": "~/.cline/skills",
        "cursor-cli": "~/.cursor/skills",
        "cursor": "~/.cursor/skills",
        "gemini-cli": "~/.gemini/skills",
        "kimi-cli": "~/.kimi/skills",
        "kiro-cli": "~/.kiro/skills",
        "kiro": "~/.kiro/skills",
        "trae": "~/.trae/skills",
        "vscode-copilot": "~/.copilot/skills",
    }

    TARGET_PATHS = {
        **OBSERVED_TARGET_PATHS,
        **OFFICIAL_TARGET_PATHS,
    }

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()

    @classmethod
    def coverage_gaps(cls) -> dict[str, list[str]]:
        declared = set(HOST_TOOL_IDS)
        target_keys = set(cls.TARGET_PATHS)
        return {
            "missing_in_skill_targets": sorted(declared - target_keys),
            "extra_in_skill_targets": sorted(target_keys - declared),
        }

    def list_targets(self) -> list[str]:
        return list(self.TARGET_PATHS.keys())

    @classmethod
    def target_path_kind(cls, target: str) -> str:
        if target in cls.OFFICIAL_TARGET_PATHS:
            return "official-user-surface"
        if target in cls.OBSERVED_TARGET_PATHS:
            return "observed-compatibility-surface"
        return "unknown"

    def skill_surface_available(self, target: str) -> bool:
        kind = self.target_path_kind(target)
        target_dir = self._target_dir(target)
        if kind == "official-user-surface":
            return True
        if kind == "observed-compatibility-surface":
            return target_dir.exists()
        return False

    def list_installed(self, target: str) -> list[str]:
        base = self._target_dir(target)
        if not base.exists():
            return []
        return sorted(
            d.name for d in base.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
        )

    def install(
        self,
        source: str,
        target: str,
        name: str | None = None,
        force: bool = False,
    ) -> SkillInstallResult:
        """安装 skill 到指定 target"""
        base = self._target_dir(target)
        base.mkdir(parents=True, exist_ok=True)

        if self._is_git_source(source):
            return self._install_from_git(source=source, target=target, name=name, force=force)

        source_path = Path(source).expanduser().resolve()
        if source_path.is_dir():
            return self._install_from_directory(
                source_dir=source_path,
                target=target,
                name=name,
                force=force,
            )

        # 内置 skill
        if source == "super-dev":
            skill_name = name or "super-dev"
            target_dir = base / skill_name
            self._prepare_target_dir(target_dir, force=force)
            self._write_builtin_skill(target_dir, skill_name, target)
            return SkillInstallResult(
                name=skill_name,
                target=target,
                path=target_dir,
                source="builtin",
            )

        raise FileNotFoundError(
            f"Skill source not found: {source}. Use a local directory, git url, or 'super-dev'."
        )

    def uninstall(self, name: str, target: str) -> Path:
        target_dir = self._target_dir(target) / name
        if not target_dir.exists():
            raise FileNotFoundError(f"Skill not found: {name} ({target})")
        shutil.rmtree(target_dir)
        return target_dir

    def _target_dir(self, target: str) -> Path:
        relative = self.TARGET_PATHS.get(target)
        if relative is None:
            raise ValueError(f"Unsupported target: {target}")
        raw_path = Path(relative).expanduser()
        if raw_path.is_absolute():
            return raw_path
        return self.project_dir / relative

    def _is_git_source(self, source: str) -> bool:
        return source.startswith("http://") or source.startswith("https://") or source.endswith(".git")

    def _validate_git_source(self, source: str) -> None:
        if source.startswith("-"):
            raise ValueError("Invalid git source")

    def _install_from_git(
        self,
        source: str,
        target: str,
        name: str | None,
        force: bool,
    ) -> SkillInstallResult:
        self._validate_git_source(source)
        git_executable = shutil.which("git")
        if not git_executable:
            raise FileNotFoundError("git executable not found in PATH")

        with tempfile.TemporaryDirectory(prefix="super-dev-skill-") as temp_dir:
            temp_path = Path(temp_dir)
            clone_dir = temp_path / "repo"
            subprocess.run(
                [git_executable, "clone", "--depth", "1", "--", source, str(clone_dir)],
                check=True,
                capture_output=True,
                text=True,
            )  # nosec B603

            skill_dirs = self._find_skill_dirs(clone_dir)
            if not skill_dirs:
                raise FileNotFoundError("No SKILL.md found in git repository")

            selected_dir = self._select_skill_dir(skill_dirs, name)
            return self._install_from_directory(
                source_dir=selected_dir,
                target=target,
                name=name or selected_dir.name,
                force=force,
            )

    def _install_from_directory(
        self,
        source_dir: Path,
        target: str,
        name: str | None,
        force: bool,
    ) -> SkillInstallResult:
        if not (source_dir / "SKILL.md").exists():
            raise FileNotFoundError(f"Directory does not contain SKILL.md: {source_dir}")

        skill_name = name or source_dir.name
        target_dir = self._target_dir(target) / skill_name
        self._prepare_target_dir(target_dir, force=force)
        shutil.copytree(source_dir, target_dir)
        return SkillInstallResult(
            name=skill_name,
            target=target,
            path=target_dir,
            source=str(source_dir),
        )

    def _prepare_target_dir(self, target_dir: Path, force: bool) -> None:
        if target_dir.exists():
            if not force:
                raise FileExistsError(f"Target skill already exists: {target_dir}")
            shutil.rmtree(target_dir)

    def _find_skill_dirs(self, root: Path) -> list[Path]:
        dirs = []
        for file_path in root.rglob("SKILL.md"):
            parent = file_path.parent
            if ".git" in parent.parts:
                continue
            dirs.append(parent)
        return dirs

    def _select_skill_dir(self, skill_dirs: list[Path], name: str | None) -> Path:
        if name is None:
            return skill_dirs[0]
        for skill_dir in skill_dirs:
            if skill_dir.name == name:
                return skill_dir
        raise FileNotFoundError(f"Skill '{name}' not found in repository")

    def _write_builtin_skill(self, target_dir: Path, skill_name: str, target: str) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        if target == "codex-cli":
            skill_content = f"""---
name: {skill_name}
description: Activate the Super Dev pipeline inside Codex CLI.
---
# {skill_name} for Codex CLI

## 触发方式（强制）

- Treat `super-dev: <需求描述>` and `super-dev：<需求描述>` as the Super Dev entry point.
- Do not treat it as ordinary chat.
- 当前宿主负责调用模型、工具、终端与实际代码修改。
- Super Dev 不是大模型平台，也不提供自己的代码生成 API。

## Runtime Contract（强制）

- Super Dev 由两部分组成：
  1. 当前项目内的本地 Python CLI 工具
  2. 当前宿主里的规则/Skill/命令映射
- 当前宿主负责调用模型、联网、终端、编辑器与实际代码修改。
- 当用户触发 `super-dev: ...` 或 `super-dev：...` 时，意味着你必须进入 Super Dev 流水线。
- 需要研究、设计、编码、运行、调试时，优先使用 Codex 自身的 web/search/terminal/edit 能力。
- 需要做治理动作时，才使用本地 `super-dev` CLI。

## 首轮响应契约（强制）

- 第一轮回复必须明确说明：Super Dev 流水线已激活，当前不是普通聊天模式。
- 第一轮回复前，优先读取 `.super-dev/WORKFLOW.md` 与 `output/*-bootstrap.md`（若存在），把其中的初始化契约视为当前仓库的显式 bootstrap 规则。
- 第一轮回复必须明确说明当前阶段是 `research`。
- 第一轮回复必须明确说明三份核心文档完成后会暂停等待用户确认。

## 本地知识库契约（强制）

- 先读取 `knowledge/`。
- 如果存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取并继承其中约束。

## Required behavior

1. First reply: say Super Dev pipeline mode is active and the current phase is `research`.
2. Before the first reply, read `.super-dev/WORKFLOW.md` and `output/*-bootstrap.md` when present and treat them as the explicit bootstrap contract for this repository.
3. Read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` when present.
4. Use Codex native web/search/edit/terminal capabilities to produce:
   - `output/*-research.md`
   - `output/*-prd.md`
   - `output/*-architecture.md`
   - `output/*-uiux.md`
5. Write the required artifacts into the repository workspace. Chat-only summaries do not count as completion.
6. Stop after the three core documents and wait for explicit confirmation.
7. Only after confirmation, create `.super-dev/changes/*/proposal.md` and `.super-dev/changes/*/tasks.md`, then continue with frontend-first implementation.
8. If the user says the UI is unsatisfactory, requests a redesign, or says the page looks AI-generated, first update `output/*-uiux.md`, then redo the frontend, rerun frontend runtime and UI review, and only then continue.
9. If the user says the architecture is wrong or the technical plan must change, first update `output/*-architecture.md`, then realign Spec/tasks and implementation before continuing.
10. If the user says quality or security is not acceptable, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue.

## Never do this

- Never jump straight into coding after `super-dev:` or `super-dev：`.
- Never create Spec or implementation work before the documents are confirmed.
- 未经用户明确确认，禁止创建 `.super-dev/changes/*`。
- Use local `super-dev` CLI for governance actions only; keep research, drafting, coding, and debugging inside Codex.

## Super Dev System Flow Contract

- SUPER_DEV_FLOW_CONTRACT_V1
- PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery
- DOC_CONFIRM_GATE: required
- PREVIEW_CONFIRM_GATE: required
- HOST_PARITY: required
"""
        else:
            skill_content = f"""---
name: {skill_name}
description: Super Dev pipeline governance for research-first, commercial-grade AI coding delivery
---
# {skill_name} - Super Dev AI Coding Skill

> 版本: 2.0.11 | 适用工具: Claude Code, Codex CLI, OpenCode, Cursor, Antigravity 等所有 AI Coding 工具

---

## Skill 角色定义

你是“**超级开发战队**”的一员，由 10 位专家协同完成流水线式 AI Coding 交付。当用户调用 Super Dev 时，你需要根据任务类型自动切换专家角色：

## 定位边界（强制）

- 当前宿主负责调用模型、工具、终端与实际代码修改。
- Super Dev 不是大模型平台，也不提供自己的代码生成 API。
- 你的职责是利用宿主现有能力，严格执行 Super Dev 的流程规范、设计约束、质量门禁与交付标准。
- 不要把 Super Dev 当作独立编码平台；真正的实现动作仍在当前宿主上下文完成。

## 触发方式（强制）

- 支持 `/super-dev` 的宿主：用户会直接输入 `/super-dev <需求描述>`。
- 不支持 `/super-dev` 的宿主：把 `super-dev: <需求描述>` 与 `super-dev：<需求描述>` 视为等效触发词。
- 当用户使用这个文本触发词时，立即进入完整的 Super Dev 流水线，而不是把它当作普通聊天内容。

## Runtime Contract（强制）

- Super Dev 由两部分组成：
  1. 当前项目内的本地 Python CLI 工具
  2. 当前宿主里的规则/Skill/命令映射
- 当前宿主负责调用模型、联网、终端、编辑器与实际代码修改。
- 当用户触发 `/super-dev ...`、`super-dev: ...` 或 `super-dev：...` 时，意味着你必须进入 Super Dev 流水线。
- 需要生成或刷新文档、Spec、质量报告、交付产物时，优先调用本地 `super-dev` CLI。
- 需要研究、设计、编码、运行、调试时，优先使用宿主自身的 browse/search/terminal/edit 能力。
- 不要等待用户解释“Super Dev 是什么”；你要把它理解为当前项目已经安装好的开发治理协议。

## 首轮响应契约（强制）

- 当用户首次输入 `/super-dev <需求描述>`、`super-dev: <需求描述>` 或 `super-dev：<需求描述>` 时，第一轮回复必须明确说明：Super Dev 流水线已激活，当前不是普通聊天模式。
- 第一轮回复前，优先读取 `.super-dev/WORKFLOW.md` 与 `output/*-bootstrap.md`（若存在），把其中的初始化契约视为当前仓库的显式 bootstrap 规则。
- 第一轮回复必须明确说明当前阶段是 `research`，并承诺先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`（若存在），再用宿主原生联网研究同类产品。
- 第一轮回复必须明确说明后续固定顺序：research -> 三份核心文档 -> 等待用户确认 -> Spec / tasks -> 前端优先并运行验证 -> 后端 / 测试 / 交付。
- 第一轮回复必须明确说明：三份核心文档完成后会暂停等待用户确认；未经确认不会创建 Spec，也不会开始编码。

## 本地知识库契约（强制）

- 当前项目如果存在 `knowledge/`，必须在 research 与文档阶段优先读取与需求相关的知识文件。
- 当前项目如果存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取其中命中的：
  - `local_knowledge`
  - `web_knowledge`
  - `research_summary`
- 命中的本地知识不是普通参考资料，而是当前项目的约束输入：
  - 标准
  - 检查清单
  - 反模式
  - 场景包
  - 质量门禁
- 这些约束必须被继承到 PRD、架构、UIUX、Spec、任务拆解和实现阶段。
- 未经用户明确确认，禁止创建 `.super-dev/changes/*`，禁止开始编码。
- research、PRD、架构、UIUX、Spec、质量报告等要求中的产物，必须真实写入项目文件，不能只在聊天里口头描述。
- 当用户明确表示 UI 不满意、要求改版、重做视觉、页面太 AI 味时，必须先更新 `output/*-uiux.md`，再重做前端，并重新执行 frontend runtime 与 UI review。
- 当用户明确表示架构不合理、模块边界错误、技术方案需要重构时，必须先更新 `output/*-architecture.md`，再同步调整 Spec / tasks 与实现方案。
- 当用户明确表示质量不达标、安全问题未解决或交付证据不完整时，必须先修复问题，重新执行 quality gate 与 `super-dev release proof-pack`，再继续后续动作。

## Super Dev System Flow Contract

- SUPER_DEV_FLOW_CONTRACT_V1
- PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery
- DOC_CONFIRM_GATE: required
- PREVIEW_CONFIRM_GATE: required
- HOST_PARITY: required
"""
        (target_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
