"""
Skill Template Engine — unified skill rendering with host-specific frontmatter.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SUPER_DEV_VERSION = "2.3.4"


@dataclass
class SkillFrontmatter:
    """标准化 skill frontmatter 字段。"""

    name: str = "super-dev"
    description: str = (
        "Super Dev pipeline governance for research-first," " commercial-grade AI coding delivery"
    )
    when_to_use: str = (
        "Use when the user says /super-dev, super-dev:, or super-dev："
        " followed by a requirement. Activate the Super Dev pipeline"
        " for research-first, commercial-grade project delivery."
    )
    allowed_tools: list[str] = field(default_factory=lambda: ["Read", "Edit", "Write", "Bash"])
    model: str | None = None
    effort: str | None = None
    context: str | None = None
    user_invocable: bool = True
    version: str = SUPER_DEV_VERSION
    paths: list[str] | None = None
    argument_hint: str | None = "requirement description"
    arguments: list[str] | None = None
    disable_model_invocation: bool = False

    def to_yaml_lines(self, host: str) -> list[str]:
        """Render frontmatter fields as YAML lines (without delimiters)."""
        lines: list[str] = []
        lines.append(f"name: {self.name}")
        lines.append(f"description: {self.description}")

        if host == "claude-code":
            lines.append(f"when-to-use: {self.when_to_use}")
            if self.allowed_tools:
                tools_str = ", ".join(self.allowed_tools)
                lines.append(f"allowed-tools: {tools_str}")
            if self.model:
                lines.append(f"model: {self.model}")
            if self.effort:
                lines.append(f"effort: {self.effort}")
            if self.context:
                lines.append(f"context: {self.context}")
            lines.append(f"user-invocable: {str(self.user_invocable).lower()}")
            lines.append(f"version: {self.version}")
            if self.paths:
                lines.append("paths:")
                for p in self.paths:
                    lines.append(f"  - {p}")
            if self.argument_hint:
                lines.append(f"argument-hint: {self.argument_hint}")
            if self.arguments:
                lines.append("arguments:")
                for a in self.arguments:
                    lines.append(f"  - {a}")
            if self.disable_model_invocation:
                lines.append("disable-model-invocation: true")
            # Runtime enforcement hook: block emoji in UI source files
            lines.append("hooks:")
            lines.append("  PreToolUse:")
            lines.append('    - matcher: "Write|Edit"')
            lines.append("      hooks:")
            lines.append("        - type: command")
            lines.append(
                '          command: "python3 -c \\"'
                "import sys,re,json;"
                "d=json.loads(sys.stdin.read());"
                "c=d.get('tool_input',{}).get('content','')or d.get('tool_input',{}).get('new_string','')or'';"
                "p=d.get('tool_input',{}).get('file_path','');"
                "e=p.rsplit('.',1)[-1]if '.' in p else'';"
                "print(json.dumps({'decision':'block','reason':'Super Dev: emoji detected in '+e+' file, use icon library'}"
                "if e in('tsx','ts','jsx','js','vue','svelte')and bool(re.search(r'[\\\\u2600-\\\\u27BF\\\\U0001F300-\\\\U0001FAFF]',c))else{}))"
                '\\"\"'
            )
            lines.append("          timeout: 5")
        elif host == "codex-cli":
            lines.append(f"when_to_use: {self.when_to_use}")
            lines.append(f"version: {self.version}")
        else:
            # Generic format — underscore keys
            lines.append(f"when_to_use: {self.when_to_use}")
            if self.allowed_tools:
                tools_str = ", ".join(self.allowed_tools)
                lines.append(f"allowed_tools: {tools_str}")
            if self.model:
                lines.append(f"model: {self.model}")
            if self.effort:
                lines.append(f"effort: {self.effort}")
            if self.context:
                lines.append(f"context: {self.context}")
            lines.append(f"user_invocable: {str(self.user_invocable).lower()}")
            lines.append(f"version: {self.version}")
            if self.paths:
                lines.append("paths:")
                for p in self.paths:
                    lines.append(f"  - {p}")
            if self.argument_hint:
                lines.append(f"argument_hint: {self.argument_hint}")
            if self.arguments:
                lines.append("arguments:")
                for a in self.arguments:
                    lines.append(f"  - {a}")
            if self.disable_model_invocation:
                lines.append("disable_model_invocation: true")

        return lines


class SuperDevSkillContent:
    """Generates the body content for a Super Dev skill file."""

    def __init__(self, skill_name: str, host: str) -> None:
        self.skill_name = skill_name
        self.host = host

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def render_body(self) -> str:
        """Return the full Markdown body (everything below the frontmatter)."""
        if self.host == "codex-cli":
            return self._render_codex_body()
        return self._render_generic_body()

    # ------------------------------------------------------------------
    # Codex CLI body
    # ------------------------------------------------------------------

    def _render_codex_body(self) -> str:
        sections = [
            f"# {self.skill_name} for Codex CLI",
            self._section_critical_reminders(),
            self._section_activation_rules_codex(),
            self._section_trigger_codex(),
            self._section_runtime_contract_codex(),
            self._section_cli_command_guide(),
            self._section_first_response_contract(),
            self._section_knowledge_contract(),
            self._section_pre_code_gate(),
            self._section_session_continuity(),
            self._section_implementation_closure(),
            self._section_phase_enforcement(),
            self._section_required_behavior_codex(),
            self._section_never_do(),
            self._section_common_mistakes(),
            self._section_error_recovery(),
            self._section_agent_teams(),
            self._section_flow_contract(),
        ]
        return "\n\n".join(sections) + "\n"

    def _section_activation_rules_codex(self) -> str:
        return (
            "## Direct Activation Rule（强制）\n"
            "\n"
            "- If this skill is invoked, Super Dev pipeline mode is already active.\n"
            "- Do not spend a turn saying you will read the skill first,"
            " explain the skill, or decide whether to enter the workflow.\n"
            '- Do not answer with variants of "我先读取 skill 再判断流程".\n'
            "- If this file is loaded from `~/.codex/skills`,"
            " treat it as the compatibility mirror of the same Super Dev contract."
        )

    def _section_trigger_codex(self) -> str:
        return (
            "## 触发方式（强制）\n"
            "\n"
            "- Treat `super-dev: <需求描述>` and `super-dev：<需求描述>`"
            " as the AGENTS-driven natural-language fallback entry point.\n"
            "- Treat `$super-dev` as the explicit official Skill mention"
            " when the Codex host exposes skills by name.\n"
            "- In Codex desktop/app, if the slash list shows this enabled skill,"
            " selecting `/super-dev` from that list is valid because it resolves"
            " to this Skill rather than a custom project slash command.\n"
            "- Do not treat it as ordinary chat.\n"
            "- 当前宿主负责调用模型、工具、终端与实际代码修改。\n"
            "- Super Dev 不是大模型平台，也不提供自己的代码生成 API。"
        )

    def _section_runtime_contract_codex(self) -> str:
        return (
            "## Runtime Contract（强制）\n"
            "\n"
            "- Super Dev 由两部分组成：\n"
            "  1. 当前项目内的本地 Python CLI 工具\n"
            "  2. 当前宿主里的规则/Skill/命令映射\n"
            "- 当前宿主负责调用模型、联网、终端、编辑器与实际代码修改。\n"
            "- 当用户通过 Codex App/Desktop 的 `/super-dev` skill 入口、"
            "Codex CLI 的 `$super-dev`，或 `super-dev: ...` / `super-dev：...`"
            " 回退入口触发时，都意味着你必须进入 Super Dev 流水线。\n"
            "- 需要研究、设计、编码、运行、调试时，"
            "优先使用 Codex 自身的 web/search/terminal/edit 能力。\n"
            "- 需要做治理动作时，才使用本地 `super-dev` CLI。"
        )

    def _section_required_behavior_codex(self) -> str:
        return (
            "## Required behavior\n"
            "\n"
            "1. First reply: say Super Dev pipeline mode is active"
            " and the current phase is `research`.\n"
            "2. Before the first reply, read `.super-dev/WORKFLOW.md`"
            " and `output/*-bootstrap.md` when present and treat them"
            " as the explicit bootstrap contract for this repository.\n"
            "3. Read `knowledge/` and"
            " `output/knowledge-cache/*-knowledge-bundle.json` when present.\n"
            "4. Use Codex native web/search/edit/terminal capabilities to produce:\n"
            "   - `output/*-research.md`\n"
            "   - `output/*-prd.md`\n"
            "   - `output/*-architecture.md`\n"
            "   - `output/*-uiux.md`\n"
            "5. Write the required artifacts into the repository workspace."
            " Chat-only summaries do not count as completion.\n"
            "6. Stop after the three core documents"
            " and wait for explicit confirmation.\n"
            "7. Only after confirmation, create"
            " `.super-dev/changes/*/proposal.md` and"
            " `.super-dev/changes/*/tasks.md`,"
            " then continue with frontend-first implementation.\n"
            "8. If the user says the UI is unsatisfactory, requests a redesign,"
            " or says the page looks AI-generated, first update"
            " `output/*-uiux.md`, then redo the frontend,"
            " rerun frontend runtime and UI review,"
            " and only then continue.\n"
            "9. If the user says the architecture is wrong"
            " or the technical plan must change, first update"
            " `output/*-architecture.md`, then realign Spec/tasks"
            " and implementation before continuing.\n"
            "10. If the user says quality or security is not acceptable,"
            " first fix the issues, rerun quality gate"
            " and `super-dev release proof-pack`,"
            " and only then continue."
        )

    # ------------------------------------------------------------------
    # Generic body (all other hosts)
    # ------------------------------------------------------------------

    def _render_generic_body(self) -> str:
        sections = [
            f"# {self.skill_name} - Super Dev AI Coding Skill",
            self._section_critical_reminders(),
            self._section_version_banner(),
            "---",
            self._section_role_definition(),
            self._section_positioning(),
            self._section_trigger_generic(),
            self._section_runtime_contract_generic(),
            self._section_cli_command_guide(),
            self._section_first_response_contract(),
            self._section_knowledge_contract(),
            self._section_pre_code_gate(),
            self._section_session_continuity(),
            self._section_implementation_closure(),
            self._section_phase_enforcement(),
            self._section_common_mistakes(),
            self._section_error_recovery(),
            self._section_agent_teams(),
            self._section_flow_contract(),
        ]
        return "\n\n".join(sections) + "\n"

    def _section_version_banner(self) -> str:
        return (
            f"> 版本: {SUPER_DEV_VERSION} | 适用工具:"
            " Claude Code, Codex CLI, OpenCode, Cursor, Antigravity 等所有 AI Coding 工具"
        )

    def _section_role_definition(self) -> str:
        return (
            "## Skill 角色定义\n"
            "\n"
            '你是"**超级开发战队**"的一员，由 11 位专家协同完成流水线式'
            " AI Coding 交付。当用户调用 Super Dev 时，"
            "你需要根据任务类型自动切换专家角色："
        )

    def _section_positioning(self) -> str:
        return (
            "## 定位边界（强制）\n"
            "\n"
            "- 当前宿主负责调用模型、工具、终端与实际代码修改。\n"
            "- Super Dev 不是大模型平台，也不提供自己的代码生成 API。\n"
            "- 你的职责是利用宿主现有能力，严格执行 Super Dev"
            " 的流程规范、设计约束、质量门禁与交付标准。\n"
            "- 不要把 Super Dev 当作独立编码平台；"
            "真正的实现动作仍在当前宿主上下文完成。"
        )

    def _section_trigger_generic(self) -> str:
        return (
            "## 触发方式与命令路由（强制）\n"
            "\n"
            "用户只需在宿主中输入 `/super-dev <参数>`。\n"
            "宿主通过 Bash 工具自动执行对应的 CLI 命令，用户无需打开终端。\n"
            "唯一需要用户在终端手动执行的命令是 `pip install super-dev`（安装/升级）。\n"
            "\n"
            "### 路由规则\n"
            "\n"
            "**规则 1 — 已知子命令 → 用 Bash 工具执行 `super-dev <完整参数>`**\n"
            "\n"
            "已知子命令完整列表：\n"
            "```\n"
            "init, bootstrap, setup, install, start, onboard, detect, doctor, migrate,\n"
            "run, status, next, continue, resume, jump, confirm,\n"
            "review, release, quality, enforce,\n"
            "spec, task, config, policy, governance, knowledge,\n"
            "memory, hooks, experts, compact,\n"
            "analyze, repo-map, impact, regression-guard, dependency-graph,\n"
            "feature-checklist, product-audit,\n"
            "create, pipeline, fix, wizard,\n"
            "generate, design, deploy, preview, expert, metrics,\n"
            "skill, integrate, update, clean, completion, feedback\n"
            "```\n"
            "\n"
            "示例：\n"
            "- `/super-dev init` → Bash: `super-dev init`\n"
            "- `/super-dev status` → Bash: `super-dev status`\n"
            "- `/super-dev run research` → Bash: `super-dev run research`\n"
            "- `/super-dev enforce validate` → Bash: `super-dev enforce validate`\n"
            "- `/super-dev quality` → Bash: `super-dev quality`\n"
            "- `/super-dev review docs --status confirmed` → Bash: `super-dev review docs --status confirmed`\n"
            "- `/super-dev release proof-pack` → Bash: `super-dev release proof-pack`\n"
            "- `/super-dev detect --auto` → Bash: `super-dev detect --auto`\n"
            "- `/super-dev setup claude-code` → Bash: `super-dev setup claude-code`\n"
            "- `/super-dev doctor --fix` → Bash: `super-dev doctor --fix`\n"
            "\n"
            "**规则 2 — 自然语言（中文/英文描述）→ 进入 pipeline 模式**\n"
            "\n"
            "示例：\n"
            "- `/super-dev 做一个电商系统`\n"
            "- `/super-dev Build a user auth system`\n"
            "- `super-dev: 做一个电商系统`（冒号触发，等效）\n"
            "- `super-dev：做一个电商系统`（中文冒号也识别）\n"
            "\n"
            "**规则 3 — 无参数 → 运行 `super-dev` 查看当前状态并继续**"
        )

    def _section_runtime_contract_generic(self) -> str:
        return (
            "## Runtime Contract（强制）\n"
            "\n"
            "- Super Dev 由两部分组成：\n"
            "  1. 当前项目内的本地 Python CLI 工具\n"
            "  2. 当前宿主里的规则/Skill/命令映射\n"
            "- 当前宿主负责调用模型、联网、终端、编辑器与实际代码修改。\n"
            "- 当用户触发 `/super-dev ...`、`super-dev: ...`"
            " 或 `super-dev：...` 时，意味着你必须进入 Super Dev 流水线。\n"
            "- 需要生成或刷新文档、Spec、质量报告、交付产物时，"
            "优先调用本地 `super-dev` CLI。\n"
            "- 需要研究、设计、编码、运行、调试时，"
            "优先使用宿主自身的 browse/search/terminal/edit 能力。\n"
            '- 不要等待用户解释"Super Dev 是什么"；'
            "你要把它理解为当前项目已经安装好的开发治理协议。"
        )

    def _section_cli_command_guide(self) -> str:
        return (
            "## Super Dev CLI 命令速查\n"
            "\n"
            "以下所有命令均在宿主内通过 `/super-dev <command>` 输入。\n"
            "宿主会通过 Bash 工具自动执行，无需打开终端。\n"
            "\n"
            "```bash\n"
            "# 项目初始化与宿主接入\n"
            "super-dev init                          # 初始化项目配置\n"
            "super-dev detect --auto                 # 探测已安装宿主\n"
            "super-dev setup <host>                  # 一步接入指定宿主\n"
            "super-dev doctor --fix                  # 诊断并修复接入问题\n"
            "super-dev migrate                       # 迁移到最新版本\n"
            "\n"
            "# 流水线控制\n"
            "super-dev run <phase>                   # 跳转到指定阶段\n"
            "super-dev status                        # 查看当前流程状态\n"
            "super-dev next                          # 推荐下一步\n"
            "super-dev continue                      # 继续当前流程\n"
            "super-dev confirm <phase>               # 确认指定阶段\n"
            "\n"
            "# 治理与质量\n"
            "super-dev enforce install               # 安装 enforcement hooks\n"
            "super-dev enforce validate              # 运行验证检查\n"
            "super-dev quality                       # 运行质量门禁\n"
            "super-dev review docs                   # 查看三文档确认状态\n"
            "super-dev review ui                     # 查看 UI 审查状态\n"
            "super-dev review preview                # 查看预览确认状态\n"
            "\n"
            "# 交付\n"
            "super-dev release proof-pack            # 生成交付证据包\n"
            "super-dev release readiness             # 发布就绪度检查\n"
            "\n"
            "# 查询\n"
            "super-dev memory list                   # 查看记忆条目\n"
            "super-dev experts list                  # 查看专家角色\n"
            "super-dev hooks list                    # 查看 hook 事件\n"
            "super-dev hooks history                 # 查看最近 hook 历史\n"
            "super-dev harness status                # 查看 workflow/framework/hook harness\n"
            "super-dev compact list                  # 查看压缩摘要\n"
            "super-dev config list                   # 查看项目配置\n"
            "super-dev spec list                     # 查看规范与变更\n"
            "```\n"
            "\n"
            "**重要**: 这些命令是治理执行层，宿主自身能力无法替代。"
        )

    # ------------------------------------------------------------------
    # Shared sections (used by both codex and generic)
    # ------------------------------------------------------------------

    def _section_critical_reminders(self) -> str:
        return (
            "## 关键约束提醒（每次操作前必读）\n"
            "\n"
            "以下规则在整个开发过程中始终有效，不得以任何理由违反：\n"
            "\n"
            "1. **图标系统**: 功能图标只能来自 Lucide / Heroicons / Tabler 图标库。"
            "绝对禁止使用 emoji 表情 作为功能图标、装饰图标或临时占位。"
            "如果你发现自己即将输出包含 emoji 的 UI 代码，停下来，改用图标库组件。\n"
            "\n"
            "2. **AI 模板化禁令**: 禁止紫/粉渐变主色调、禁止 emoji 图标、"
            "禁止无信息层级的卡片墙、禁止默认系统字体直出。\n"
            "\n"
            "3. **代码即交付**: 不允许\u201c先用 emoji 顶上后面再换\u201d。"
            "图标库必须在第一行 UI 代码前就锁定。\n"
            "\n"
            "4. **自检规则**: 在向用户展示任何 UI 代码或预览前，"
            "必须自检源码中不存在任何 emoji 字符"
            "（Unicode range U+2600-U+27BF, U+1F300-U+1FAFF）。"
            "发现后先替换为正式图标库再继续。"
        )

    def _section_first_response_contract(self) -> str:
        return (
            "## 首轮响应契约（强制）\n"
            "\n"
            "- 首次触发时第一轮回复必须说明：流水线已激活，当前阶段是 `research`。\n"
            "- 先读取 `.super-dev/WORKFLOW.md` 与 `output/*-bootstrap.md`（若存在）。\n"
            "- 说明固定顺序：research -> 三份核心文档 -> 等待确认"
            " -> Spec/tasks -> 前端优先 -> 后端/测试/交付。\n"
            "- 三份核心文档完成后暂停等待确认；未经确认不创建 Spec 也不编码。\n"
            "\n"
            "### research 双引擎\n"
            "\n"
            "**引擎 1: CLI 知识推送** — `super-dev run research`"
            " 触发本地知识发现，读取 `knowledge/` 和 knowledge-bundle.json。\n"
            "\n"
            "**引擎 2: 宿主联网研究** — WebFetch/WebSearch 搜索同类产品、"
            "竞品和官方文档，写入 `output/*-research.md`。\n"
            "\n"
            "两个引擎的结果都必须在 PRD/架构/UIUX 文档中被继承。"
        )

    def _section_knowledge_contract(self) -> str:
        return (
            "## 本地知识库契约（强制）\n"
            "\n"
            "- 存在 `knowledge/` 时，research 与文档阶段优先读取相关知识文件。\n"
            "- 存在 `output/knowledge-cache/*-knowledge-bundle.json` 时，"
            "先读取 local_knowledge / web_knowledge / research_summary。\n"
            "- 命中的知识是项目约束（标准/检查清单/反模式/场景包/质量门禁），"
            "必须继承到 PRD、架构、UIUX、Spec 和实现阶段。\n"
            "- 未经用户确认禁止创建 `.super-dev/changes/*` 或开始编码。\n"
            "- 产物必须真实写入项目文件，不能只在聊天中口头描述。"
        )

    def _section_session_continuity(self) -> str:
        return (
            "## 会话连续性契约（强制）\n"
            "\n"
            "- 若存在 `.super-dev/SESSION_BRIEF.md`，每次继续前必须先读取。\n"
            '- 用户在确认门/返工门说"改/补充/确认/继续"等，属于流程内动作，不退回普通聊天。\n'
            "- 修改后留在当前门里，总结变化并再次等待确认。\n"
            "- UI 不满意 -> 先更新 `output/*-uiux.md`，再重做前端 + UI review。\n"
            "- 架构不合理 -> 先更新 `output/*-architecture.md`，再调整 Spec/实现。\n"
            "- 质量不达标 -> 先修复，重新执行 quality gate + proof-pack。\n"
            "- 启用 policy 时不得默认建议降低治理强度。"
        )

    def _section_pre_code_gate(self) -> str:
        return (
            "## 编码前门禁（Spec 确认后、编码开始前必须执行）\n"
            "\n"
            "跳过任何一步都会导致大量返工：\n"
            "\n"
            "### 第 1 步：技术栈预研（最关键）\n"
            "- 读取项目依赖文件（package.json / requirements.txt / go.mod 等），"
            "找到主要依赖的精确版本号\n"
            "- 用 WebFetch 查阅每个主要框架的官方文档："
            "Getting Started、Migration Guide、API Reference\n"
            "- **不确定 API 写法时，先查官方文档再写代码，永远不要猜**\n"
            "\n"
            "### 第 2 步：读取项目配置\n"
            "- `super-dev.yaml` 确认技术栈选择\n"
            "- 框架配置文件、tsconfig.json、.env.example\n"
            "- 已有代码目录结构\n"
            "\n"
            "### 第 3 步：声明 UI 工具链\n"
            "- 声明并确认图标库（Lucide/Heroicons/Tabler）和组件库已安装\n"
            "- 不声明 = 不允许写 UI 代码\n"
            "\n"
            "### 第 4 步：确认 API 契约和设计 token\n"
            "- 读取 output/*-architecture.md 中的 API 定义\n"
            "- 读取 output/*-uiux.md 中的设计 token\n"
            "\n"
            "### 第 5 步：生成脚手架并验证构建\n"
            "- `super-dev generate components` + `super-dev generate types`\n"
            "- 运行构建命令确认零错误后才开始写业务代码\n"
        )

    def _section_phase_enforcement(self) -> str:
        return (
            "## 编码阶段持续治理\n"
            "\n"
            "读取 `.super-dev/pipeline-state.json` 了解当前在哪个阶段。\n"
            "根据阶段调整你的工作重点：research 阶段侧重调研，frontend 阶段侧重 UI 实现，"
            "quality 阶段侧重测试和门禁。\n"
            "\n"
            "每次进入新阶段时宣告: `Super Dev | [N/9] 阶段名 开始 | 主导专家: XXX`\n"
            "\n"
            "### 每次写文件前自检\n"
            '- [ ] "use client" 是否需要？（Next.js）\n'
            "- [ ] 图标来自声明的图标库？（不是 emoji）\n"
            "- [ ] 颜色来自设计 token？（不是硬编码 hex）\n"
            "- [ ] import 路径正确？API 路径与架构文档一致？\n"
            "\n"
            "### 每完成一个功能后\n"
            "1. build 无错误 2. lint 无 error 3. 无控制台红色错误\n"
            "4. 对比 output/*-uiux.md 视觉一致 5. 运行 validate-superdev.sh（如有）"
        )

    def _section_common_mistakes(self) -> str:
        blocks: list[str] = [
            "## 宿主常犯错误速查（每次编码前扫一眼）",
        ]

        # Top 3 with code examples
        blocks.append(
            "### 错误 1: 使用 emoji 作为图标\n"
            "```tsx\n"
            "// ❌ <button>🔍 搜索</button>\n"
            "// ✅ import { Search } from 'lucide-react'\n"
            "//    <button><Search size={16} /> 搜索</button>\n"
            "```"
        )

        blocks.append(
            "### 错误 2: 紫色渐变 AI 模板\n"
            "```tsx\n"
            "// ❌ bg-gradient-to-r from-purple-500 to-pink-500\n"
            "// ✅ 使用 output/*-uiux.md 定义的品牌色: bg-primary + text-heading-1\n"
            "```"
        )

        blocks.append(
            "### 错误 3: 前后端 API 路径不一致\n"
            "```\n"
            "// ❌ 架构文档写 /api/users，后端实际是 /api/v1/users\n"
            "// ✅ 编码前先确认 output/*-architecture.md 中的 API 路径\n"
            "```"
        )

        # Next.js: one-liner summaries
        if self._is_nextjs_likely():
            blocks.append(
                "### Next.js 常见错误（一行速查）\n"
                "- 用 `<img>` 而非 `next/image` Image 组件\n"
                "- 用 `<a>` 而非 `next/link` Link 组件\n"
                "- 在 Server Component 中使用 useState/useEffect（需 `'use client'` 或改 async）\n"
                "- 用 Express 风格 handler(req,res) 而非 Route Handler export async function GET()"
            )

        return "\n\n".join(blocks)

    def _is_nextjs_likely(self) -> bool:
        """Check if the project is likely using Next.js based on skill name/host hints."""
        name_lower = self.skill_name.lower()
        return "next" in name_lower or "nextjs" in name_lower

    def _section_implementation_closure(self) -> str:
        return (
            "## 实现闭环契约（强制）\n"
            "\n"
            "- 每轮修改后先做最小 diff review 再汇报完成。\n"
            "- 运行 build / type-check / test / runtime smoke。\n"
            "- 新增代码必须接入真实调用链；未接入则删除，禁止留 unused code。\n"
            "- 新增日志/告警/埋点必须验证会在真实路径触发。"
        )

    def _section_never_do(self) -> str:
        return (
            "## Never do this\n"
            "\n"
            "- Never jump straight into coding"
            " after `super-dev:` or `super-dev：`.\n"
            "- Never create Spec or implementation work"
            " before the documents are confirmed.\n"
            "- 未经用户明确确认，禁止创建 `.super-dev/changes/*`。\n"
            "- Use local `super-dev` CLI for governance actions only;"
            " keep research, drafting, coding, and debugging inside"
            f" {self._host_display_name()}."
        )

    def _section_error_recovery(self) -> str:
        return (
            "## 错误恢复策略\n"
            "\n"
            "遇到错误时按以下优先级恢复：\n"
            "\n"
            "**阶段 1 -- 便宜恢复（不丢失上下文）**\n"
            '- Token 超限？注入"继续，不要回顾"然后重试\n'
            "- 工具失败？注入错误详情 + 备选方案，继续\n"
            "- 权限拒绝？说明允许什么，继续\n"
            "\n"
            "**阶段 2 -- 上下文重建（可能丢失细节）**\n"
            "- Prompt 过长？压缩旧上下文，保留最近内容\n"
            "- 多次失败？丢弃非关键历史，只保留关键决策\n"
            "\n"
            "**阶段 3 -- 暴露错误（无法恢复）**\n"
            "- 提供: 什么失败了 + 为什么 + 下一步建议\n"
            "- 运行 `super-dev doctor --fix` 尝试自动修复\n"
            "\n"
            "永远不要在尝试阶段 1-2 之前就暴露错误给用户。"
        )

    def _section_agent_teams(self) -> str:
        return (
            "## Agent Teams 协作（支持 Teams 功能的宿主）\n"
            "\n"
            "如果宿主支持 Agent Teams（如 Claude Code 的 /teams），"
            "可以让多位 Super Dev 专家并行工作：\n"
            "\n"
            "**研究阶段**: PM + ARCHITECT 并行调研\n"
            "**文档阶段**: PRD / Architecture / UIUX 可并行起草\n"
            "**编码阶段**: 前端 + 后端可并行开发（注意 API 契约对齐）\n"
            "**质量阶段**: Security + QA + Performance 并行审查\n"
            "\n"
            "使用 Teams 时的约束：\n"
            "- 每个 teammate 必须声明自己的专家角色\n"
            "- teammates 之间通过共享文件（output/*.md）传递上下文\n"
            "- 修改同一文件前必须协调（避免冲突）\n"
            "- 质量门禁结果必须等所有 teammates 完成后汇总"
        )

    def _section_flow_contract(self) -> str:
        return (
            "## Super Dev System Flow Contract\n"
            "\n"
            "- SUPER_DEV_FLOW_CONTRACT_V1\n"
            "- PHASE_CHAIN: research>docs>docs_confirm>spec>"
            "frontend>preview_confirm>backend>quality>delivery\n"
            "- DOC_CONFIRM_GATE: required\n"
            "- PREVIEW_CONFIRM_GATE: required\n"
            "- HOST_PARITY: required"
        )

    def _host_display_name(self) -> str:
        display_map = {
            "codex-cli": "Codex",
            "claude-code": "Claude Code",
            "cursor": "Cursor",
            "cursor-cli": "Cursor",
            "windsurf": "Windsurf",
        }
        return display_map.get(self.host, "the host")


class SkillTemplate:
    """Renders a complete SKILL.md file from frontmatter + body content."""

    def __init__(
        self,
        frontmatter: SkillFrontmatter,
        content: SuperDevSkillContent,
    ) -> None:
        self.frontmatter = frontmatter
        self.content = content

    def render(self, host: str) -> str:
        """Render the full SKILL.md content for the given host."""
        fm_lines = self.frontmatter.to_yaml_lines(host)
        fm_block = "---\n" + "\n".join(fm_lines) + "\n---"
        body = self.content.render_body()
        return fm_block + "\n" + body

    @classmethod
    def for_builtin(cls, skill_name: str, host: str) -> SkillTemplate:
        """Factory: create a template pre-configured for the built-in skill."""
        if host == "codex-cli":
            fm = SkillFrontmatter(
                name=skill_name,
                description="Activate the Super Dev pipeline inside Codex CLI.",
            )
        else:
            fm = SkillFrontmatter(
                name=skill_name,
                description=(
                    "Super Dev pipeline governance for research-first,"
                    " commercial-grade AI coding delivery"
                ),
            )
        content = SuperDevSkillContent(skill_name=skill_name, host=host)
        return cls(frontmatter=fm, content=content)
