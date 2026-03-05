"""
多平台 AI Coding 工具集成管理器
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from ..catalogs import HOST_TOOL_CATEGORY_MAP, HOST_TOOL_IDS


@dataclass
class IntegrationTarget:
    name: str
    description: str
    files: list[str]


@dataclass
class HostAdapterProfile:
    host: str
    category: str
    adapter_mode: str
    host_model_provider: str
    official_docs_url: str
    docs_verified: bool
    primary_entry: str
    terminal_entry: str
    terminal_entry_scope: str
    integration_files: list[str]
    slash_command_file: str
    skill_dir: str
    detection_commands: list[str]
    detection_paths: list[str]
    notes: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class IntegrationManager:
    """为不同 AI Coding 平台生成集成配置"""

    TARGETS: dict[str, IntegrationTarget] = {
        "claude-code": IntegrationTarget(
            name="claude-code",
            description="Claude Code CLI 深度集成",
            files=[".claude/CLAUDE.md"],
        ),
        "codex-cli": IntegrationTarget(
            name="codex-cli",
            description="Codex CLI 项目上下文注入",
            files=[".codex/AGENTS.md"],
        ),
        "gemini-cli": IntegrationTarget(
            name="gemini-cli",
            description="Gemini CLI 项目规则注入",
            files=[".gemini/AGENTS.md"],
        ),
        "kimi-cli": IntegrationTarget(
            name="kimi-cli",
            description="Kimi CLI 项目规则注入",
            files=[".kimi/AGENTS.md"],
        ),
        "kiro-cli": IntegrationTarget(
            name="kiro-cli",
            description="Kiro CLI 项目规则注入",
            files=[".kiro/AGENTS.md"],
        ),
        "qoder-cli": IntegrationTarget(
            name="qoder-cli",
            description="Qoder CLI 项目规则注入",
            files=[".qoder/AGENTS.md"],
        ),
        "qoder": IntegrationTarget(
            name="qoder",
            description="Qoder IDE 规则注入",
            files=[".qoder/rules.md"],
        ),
    }
    SLASH_COMMAND_FILES: dict[str, str] = {
        "claude-code": ".claude/commands/super-dev.md",
        "codex-cli": ".codex/commands/super-dev.md",
        "gemini-cli": ".gemini/commands/super-dev.md",
        "kimi-cli": ".kimi/commands/super-dev.md",
        "kiro-cli": ".kiro/commands/super-dev.md",
        "qoder-cli": ".qoder/commands/super-dev.md",
        "qoder": ".qoder/commands/super-dev.md",
    }
    OFFICIAL_DOCS: dict[str, str] = {
        "claude-code": "https://docs.anthropic.com/en/docs/claude-code/slash-commands",
        "codex-cli": "https://platform.openai.com/docs/codex",
        "gemini-cli": "https://google-gemini.github.io/gemini-cli/docs/",
        "kimi-cli": "https://kimi.com/code/docs/cli/reference",
        "kiro-cli": "https://kiro.dev/docs/cli/",
        "qoder-cli": "https://docs.qoder.com/cli/using-cli",
        "qoder": "https://docs.qoder.com/user-guide/rules",
    }
    DOCS_VERIFIED_TARGETS: set[str] = {key for key, value in OFFICIAL_DOCS.items() if bool(value)}

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.templates_dir = self.project_dir / "templates"

    @classmethod
    def coverage_gaps(cls) -> dict[str, list[str]]:
        declared = set(HOST_TOOL_IDS)
        target_keys = set(cls.TARGETS)
        slash_keys = set(cls.SLASH_COMMAND_FILES)
        docs_keys = set(cls.OFFICIAL_DOCS)
        verified_keys = set(cls.DOCS_VERIFIED_TARGETS)
        declared_with_docs = {item for item, value in cls.OFFICIAL_DOCS.items() if bool(value)}
        return {
            "missing_in_targets": sorted(declared - target_keys),
            "extra_in_targets": sorted(target_keys - declared),
            "missing_in_slash": sorted(declared - slash_keys),
            "extra_in_slash": sorted(slash_keys - declared),
            "missing_in_docs_map": sorted(declared - docs_keys),
            "extra_in_docs_map": sorted(docs_keys - declared),
            "missing_official_docs_url": sorted(declared - declared_with_docs),
            "unverified_docs": sorted(declared - verified_keys),
        }

    def list_targets(self) -> list[IntegrationTarget]:
        return list(self.TARGETS.values())

    def get_adapter_profile(self, target: str) -> HostAdapterProfile:
        from ..catalogs import HOST_COMMAND_CANDIDATES, HOST_PATH_PATTERNS
        from ..skills import SkillManager

        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        category = HOST_TOOL_CATEGORY_MAP.get(target, "ide")
        integration_files = list(self.TARGETS[target].files)
        slash_file = self.SLASH_COMMAND_FILES.get(target, "")
        skill_dir = SkillManager.TARGET_PATHS.get(target, "")
        docs_url = self.OFFICIAL_DOCS.get(target, "")
        docs_verified = target in self.DOCS_VERIFIED_TARGETS
        adapter_mode = self._adapter_mode(target=target, category=category, integration_files=integration_files)

        if category == "cli":
            primary_entry = '/super-dev "<需求描述>"（在该 CLI 宿主会话内）'
            notes = "CLI 宿主建议直接在当前会话执行 slash 命令。"
        else:
            primary_entry = '/super-dev "<需求描述>"（在 IDE Agent Chat 内）'
            notes = "IDE 宿主优先通过 Agent Chat 触发，保持上下文连续。"

        return HostAdapterProfile(
            host=target,
            category=category,
            adapter_mode=adapter_mode,
            host_model_provider="host",
            official_docs_url=docs_url,
            docs_verified=docs_verified,
            primary_entry=primary_entry,
            terminal_entry='super-dev "<需求描述>"',
            terminal_entry_scope="仅触发本地编排，不直接调用宿主模型会话",
            integration_files=integration_files,
            slash_command_file=slash_file,
            skill_dir=skill_dir,
            detection_commands=list(HOST_COMMAND_CANDIDATES.get(target, [])),
            detection_paths=list(HOST_PATH_PATTERNS.get(target, [])),
            notes=notes,
        )

    def list_adapter_profiles(self, targets: list[str] | None = None) -> list[HostAdapterProfile]:
        selected = targets or sorted(self.TARGETS.keys())
        return [self.get_adapter_profile(target) for target in selected]

    def _adapter_mode(self, *, target: str, category: str, integration_files: list[str]) -> str:
        first_file = integration_files[0] if integration_files else ""
        if category == "cli":
            return "native-cli-session"
        if first_file.startswith(".super-dev/skills/"):
            return "compat-layer-via-project-skill"
        if target == "vscode-copilot":
            return "native-copilot-instruction-file"
        if target == "jetbrains-ai":
            return "native-jetbrains-ai-prompt-config"
        return "native-ide-rule-file"

    def setup(self, target: str, force: bool = False) -> list[Path]:
        if target not in self.TARGETS:
            raise ValueError(f"Unsupported target: {target}")

        written_files: list[Path] = []
        integration = self.TARGETS[target]
        for relative in integration.files:
            file_path = self.project_dir / relative
            if file_path.exists() and not force:
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = self._build_content(target=target)
            file_path.write_text(content, encoding="utf-8")
            written_files.append(file_path)

        return written_files

    def setup_all(self, force: bool = False) -> dict[str, list[Path]]:
        result: dict[str, list[Path]] = {}
        for target in self.TARGETS:
            result[target] = self.setup(target=target, force=force)
        return result

    def setup_slash_command(self, target: str, force: bool = False) -> Path | None:
        relative = self.SLASH_COMMAND_FILES.get(target)
        if relative is None:
            raise ValueError(f"Unsupported target: {target}")
        command_file = self.project_dir / relative
        if command_file.exists() and not force:
            return None
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_file.write_text(self._build_slash_command_content(target), encoding="utf-8")
        return command_file

    def setup_all_slash_commands(self, force: bool = False) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {}
        for target in self.TARGETS:
            result[target] = self.setup_slash_command(target=target, force=force)
        return result

    def _build_content(self, target: str) -> str:
        if target == "cursor":
            cursor_template = self.templates_dir / ".cursorrules.template"
            if cursor_template.exists():
                body = cursor_template.read_text(encoding="utf-8")
                return (
                    f"{body}\n\n"
                    "# Super Dev Pipeline Rules\n"
                    "- Always read output/*-prd.md, output/*-architecture.md, output/*-uiux.md first.\n"
                    "- Execute frontend-first delivery before backend/database tasks.\n"
                    "- Meet the active quality gate threshold before release.\n"
                )

        if target == "antigravity":
            return self._antigravity_workflow_rules()

        if target in {
            "cursor",
            "windsurf",
            "cline",
            "continue",
            "vscode-copilot",
            "jetbrains-ai",
            "roo-code",
            "augment",
            "qoder",
            "trae",
            "codebuddy",
            "tongyi-lingma",
            "codegeex",
        }:
            return self._generic_ide_rules(target)

        if target in {
            "codex-cli",
            "opencode",
            "gemini-cli",
            "kiro-cli",
            "cursor-cli",
            "qoder-cli",
            "codebuddy-cli",
            "iflow",
            "aider",
        }:
            return self._generic_cli_rules(target)

        if target == "claude-code":
            return self._claude_rules()

        return self._generic_cli_rules(target)

    def _build_slash_command_content(self, target: str) -> str:
        return (
            f"# /super-dev ({target})\n\n"
            "在当前项目触发 Super Dev 流水线。\n\n"
            "## 定位\n"
            "- Super Dev 本身不提供模型能力，不调用外部模型 API。\n"
            "- 代码生成/修改能力完全来自当前宿主（Claude/Codex/Gemini/IDE Agent）。\n"
            "- Super Dev 只负责流程规范、门禁与审计。\n\n"
            "## 用法\n"
            "/super-dev <需求描述>\n\n"
            "## 终端替代入口（仅本地编排）\n"
            "```bash\n"
            "super-dev \"<需求描述>\"\n"
            "```\n\n"
            "## 建议\n"
            "- 宿主会话运行目录应为项目根目录。\n"
            "- 终端入口不直接调用宿主模型会话，代码生成与修改仍在宿主中完成。\n"
        )

    def _generic_cli_rules(self, target: str) -> str:
        return (
            f"# Super Dev Integration for {target}\n\n"
            "Super Dev 是“超级开发战队”，一个流水线式 AI Coding 辅助工具。\n"
            "Super Dev does not provide model inference or coding APIs.\n"
            "Use the host model/runtime as-is; Super Dev only enforces the delivery protocol.\n"
            "Use Super Dev generated artifacts as source of truth.\n\n"
            "## Trigger\n"
            '- Preferred: `/super-dev "<需求描述>"`\n'
            '- Terminal entry (local orchestration only): `super-dev "<需求描述>"`\n'
            "- Terminal entry does not directly talk to the host model session.\n\n"
            "## Required Context\n"
            "- output/*-prd.md\n"
            "- output/*-architecture.md\n"
            "- output/*-uiux.md\n"
            "- output/*-execution-plan.md\n"
            "- .super-dev/changes/*/tasks.md\n\n"
            "## Execution Order\n"
            "1. Implement frontend modules first\n"
            "2. Implement backend APIs and data layer\n"
            "3. Run tests and quality gate\n"
            "4. Prepare CI/CD and release\n"
        )

    def _generic_ide_rules(self, target: str) -> str:
        return (
            f"# Super Dev IDE Rules ({target})\n\n"
            "## Positioning\n"
            "- Super Dev is a host-level workflow governor, not an LLM platform.\n"
            "- Keep using the host's model capabilities; do not expect extra model APIs from Super Dev.\n\n"
            "## Working Agreement\n"
            "- Read generated documents before coding.\n"
            "- Respect Spec tasks sequence.\n"
            "- Keep architecture and UIUX consistency.\n\n"
            "## Delivery Criteria\n"
            "- Frontend can be demonstrated early.\n"
            "- Backend and migration scripts match specs.\n"
            "- Security/performance checks are resolved.\n"
            "- Quality gate threshold is met for the current scenario.\n"
        )

    def _claude_rules(self) -> str:
        return (
            "# Super Dev Claude Code Integration\n\n"
            "This project uses a pipeline-driven development model.\n\n"
            "## Positioning\n"
            "- Super Dev does not own a model endpoint.\n"
            "- Claude Code remains the execution host for coding capability.\n"
            "- Super Dev provides governance: protocol, gates, and audit artifacts.\n\n"
            "## Before coding\n"
            "1. Read output/*-prd.md\n"
            "2. Read output/*-architecture.md\n"
            "3. Read output/*-uiux.md\n"
            "4. Read output/*-execution-plan.md\n"
            "5. Follow .super-dev/changes/*/tasks.md\n\n"
            "## Output Quality\n"
            "- Keep security/performance constraints from red-team report.\n"
            "- Ensure quality gate threshold is met before merge.\n"
        )

    def _antigravity_workflow_rules(self) -> str:
        """
        生成 Antigravity IDE 专属工作流配置。
        文件写入 .agents/workflows/super-dev.md，
        格式遵循 Antigravity Skill YAML frontmatter + markdown 规范。
        """
        return """\
---
description: Super Dev 流水线式 AI Coding 辅助工作流 - 从需求到交付的 12 阶段自动化流程
---

# Super Dev Pipeline Workflow

## 角色定义

本工作流激活 10 位专家角色自动协作：

| 专家 | 职责 |
|:---|:---|
| PM | 需求分析、PRD 生成、用户故事 |
| ARCHITECT | 架构设计、技术选型、API 契约 |
| UI/UX | 设计系统、交互规范、原型设计 |
| SECURITY | 红队审查、OWASP 检测、威胁建模 |
| CODE | 代码实现、最佳实践、代码审查 |
| DBA | 数据库设计、迁移脚本、索引优化 |
| QA | 测试策略、质量门禁、覆盖率要求 |
| DEVOPS | CI/CD 配置、容器化、监控告警 |
| RCA | 根因分析、故障复盘、风险识别 |

## 工作流步骤

### 前置：读取必备文档

在写任何一行代码前，必须先读取：

1. `output/*-prd.md` — 产品需求和验收标准
2. `output/*-architecture.md` — 技术栈和 API 设计
3. `output/*-uiux.md` — 设计系统和组件规范
4. `output/*-execution-plan.md` — 阶段任务路线图
5. `.super-dev/changes/*/tasks.md` — 具体实现任务清单

### 第 0 阶段：需求增强

```bash
super-dev "你的需求描述"
```

- 解析自然语言需求，注入领域知识库
- 联网检索补充市场和技术背景
- 输出结构化需求蓝图

### 第 1 阶段：专业文档生成

自动生成：
- `output/*-prd.md` — PRD（产品需求文档）
- `output/*-architecture.md` — 架构设计文档
- `output/*-uiux.md` — UI/UX 设计文档

### 第 2-4 阶段：骨架构建

- 前端可演示骨架（前端先行原则）
- Spec 规范（结构化规范风格）
- 前后端实现骨架 + API 契约

### 第 5-6 阶段：质量保障

- 红队审查（安全 + 性能 + 架构）
- 质量门禁（统一标准：80+）

### 第 7-8 阶段：交付准备

- 代码审查指南
- AI 提示词生成（直接传给 AI 开始开发）

### 第 9-11 阶段：部署与交付

- CI/CD 配置（GitHub/GitLab/Jenkins/Azure/Bitbucket）
- 数据库迁移脚本（Prisma/TypeORM/SQLAlchemy 等 6 种 ORM）
- 项目交付包（manifest + report + zip）

## 执行规则

- **前端先行**：先完成可演示前端，再实现后端 API
- **禁止 emoji 图标**：使用 Lucide/Heroicons/Tabler Icons
- **参数化查询**：禁止字符串拼接 SQL
- **任务跟踪**：每完成一项在 tasks.md 标记 `[x]`
- **质量门禁**：交付前运行 `super-dev quality --type all`

## 常用命令

```bash
super-dev "需求"               # 完整 12 阶段流水线（推荐）
super-dev pipeline "需求"      # 高级参数模式
super-dev create "需求"        # 生成文档 + Spec
super-dev quality --type all   # 质量检查
super-dev expert SECURITY "需求"  # 单专家调用
super-dev skill install super-dev --target antigravity  # 安装 Skill
```
"""
