"""IntegrationManager content builder mixin helpers."""

from __future__ import annotations

from pathlib import Path


class IntegrationManagerContentMixin:
    def _conversation_continuity_contract_en(self) -> str:
        return (
            "## Conversation Continuity Contract\n"
            "- If `.super-dev/SESSION_BRIEF.md` exists, read it before responding and treat it as the active workflow state.\n"
            "- If the workflow is waiting for docs confirmation, preview confirmation, UI revision, architecture revision, or quality revision, then user replies like `修改`, `补充`, `继续改`, `确认`, `通过`, `继续`, or detailed feedback remain inside the current Super Dev stage.\n"
            "- After each requested revision inside a gate, stay in the same stage, update the required artifacts, summarize what changed, and wait again for explicit confirmation.\n"
            "- Do not silently exit Super Dev mode because the user asked for several edits, follow-up questions, or extra constraints.\n"
            "- Only leave the current Super Dev workflow if the user explicitly says to cancel the workflow, restart from scratch, or switch back to normal chat.\n\n"
        )

    def _build_kiro_global_steering_content(self) -> str:
        return (
            "# Super Dev Global Steering\n\n"
            "This global steering file activates Super Dev governance for Kiro workspaces that opt into the pipeline.\n\n"
            "## Activation\n"
            "- When the user types `super-dev: ...`, enter the Super Dev workflow immediately.\n"
            "- Treat project-local `.kiro/steering/super-dev.md` as the project-specific source of truth.\n\n"
            "## Required Sequence\n"
            "1. Research first\n"
            "2. Draft PRD, architecture, and UIUX\n"
            "3. Stop for user confirmation\n"
            "4. Create Spec/tasks only after confirmation\n"
            "5. Frontend runtime verification before backend and delivery\n\n"
            "## Boundary\n"
            "- Kiro remains the execution host.\n"
            "- Super Dev is the governance layer and local Python tooling, not a separate model platform.\n"
        )

    def setup_all(self, force: bool = False) -> dict[str, list[Path]]:
        result: dict[str, list[Path]] = {}
        for target in self.TARGETS:
            result[target] = self.setup(target=target, force=force)
        return result

    def _upsert_managed_block(
        self,
        *,
        file_path: Path,
        begin: str,
        end: str,
        block_content: str,
    ) -> bool:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        existing = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        managed = f"{begin}\n{block_content.rstrip()}\n{end}\n"
        if begin in existing and end in existing:
            start = existing.index(begin)
            stop = existing.index(end, start) + len(end)
            updated = f"{existing[:start]}{managed}{existing[stop:]}"
        elif existing.strip():
            spacer = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
            updated = f"{existing}{spacer}{managed}"
        else:
            updated = managed
        if updated == existing:
            return False
        file_path.write_text(updated, encoding="utf-8")
        return True

    def _remove_managed_block(
        self,
        *,
        file_path: Path,
        begin: str,
        end: str,
    ) -> bool:
        if not file_path.exists():
            return False
        existing = file_path.read_text(encoding="utf-8")
        if begin not in existing or end not in existing:
            return False
        start = existing.index(begin)
        stop = existing.index(end, start) + len(end)
        if stop < len(existing) and existing[stop:stop + 1] == "\n":
            stop += 1
        updated = existing[:start] + existing[stop:]
        updated = updated.strip()
        if not updated:
            file_path.unlink(missing_ok=True)
            return True
        file_path.write_text(updated + "\n", encoding="utf-8")
        return True

    def setup_slash_command(self, target: str, force: bool = False) -> Path | None:
        return self.setup_slash_command_for_scope(target=target, force=force, scope="project")

    def setup_global_slash_command(self, target: str, force: bool = False) -> Path | None:
        return self.setup_slash_command_for_scope(target=target, force=force, scope="global")

    def setup_slash_command_for_scope(self, target: str, force: bool = False, scope: str = "project") -> Path | None:
        if not self.supports_slash(target):
            return None
        command_file = self.resolve_slash_command_path(
            target=target,
            scope=scope,
            project_dir=self.project_dir,
        )
        if command_file.exists() and not force:
            return None
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_content = self._append_flow_contract(
            content=self._build_slash_command_content(target),
            relative=command_file.name,
        )
        command_file.write_text(command_content, encoding="utf-8")
        return command_file

    @classmethod
    def resolve_slash_command_path(
        cls,
        *,
        target: str,
        scope: str,
        project_dir: Path | None = None,
    ) -> Path:
        if not cls.supports_slash(target):
            raise ValueError(f"Unsupported target: {target}")

        if scope == "project":
            if project_dir is None:
                raise ValueError("project_dir is required when scope='project'")
            relative = cls.SLASH_COMMAND_FILES[target]
            return Path(project_dir).resolve() / relative

        if scope == "global":
            relative = cls.GLOBAL_SLASH_COMMAND_FILES.get(target, cls.SLASH_COMMAND_FILES[target])
            return Path.home() / relative

        raise ValueError(f"Unsupported slash scope: {scope}")

    @classmethod
    def supports_slash(cls, target: str) -> bool:
        return target in cls.SLASH_COMMAND_FILES and target not in cls.NO_SLASH_TARGETS

    @classmethod
    def requires_skill(cls, target: str) -> bool:
        return target not in cls.NO_SKILL_TARGETS

    def setup_all_slash_commands(self, force: bool = False) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {}
        for target in self.TARGETS:
            result[target] = self.setup_slash_command(target=target, force=force)
        return result

    def _build_content(self, target: str) -> str:
        return self._build_file_content(target=target, relative="")

    def _build_file_content(self, target: str, relative: str) -> str:
        if target == "codex-cli" and relative == "AGENTS.md":
            return self._build_codex_agents_content()

        if target == "claude-code" and relative.endswith(".claude/agents/super-dev-core.md"):
            return self._build_claude_agent_content()

        if target == "codebuddy" and relative.endswith(".codebuddy/agents/super-dev-core.md"):
            return self._build_codebuddy_agent_content()

        if target == "trae":
            return self._trae_rules()

        if relative.endswith("/skills/super-dev-core/SKILL.md"):
            return self._build_embedded_skill_content()

        if target in {"cursor", "cursor-cli"}:
            rules_body = (
                "# Super Dev Pipeline Rules\n"
                "- When the user triggers `/super-dev ...`, enter Super Dev pipeline mode immediately.\n"
                "- Start with research and write output/*-research.md as a real file in the repository.\n"
                "- Always read and maintain output/*-prd.md, output/*-architecture.md, and output/*-uiux.md as source-of-truth project files.\n"
                "- Summarize the three core documents to the user and wait for user confirmation before creating Spec/tasks or writing code.\n"
                "- Create Spec/tasks only after confirmation.\n"
                "- Execute frontend-first delivery before backend/database tasks, then run quality gate before release.\n"
                "- Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from output/*-uiux.md.\n"
                "- Do not use emoji as functional icons or placeholders.\n"
                "- For non-conversational AI products, avoid Claude / ChatGPT-style sidebar chat shells unless the UI plan explicitly justifies them.\n"
                "- Keep using the component ecosystem and design token direction defined in output/*-uiux.md rather than switching ad hoc.\n"
                "- If `.super-dev/SESSION_BRIEF.md` exists, read it before responding and keep the current Super Dev gate active across follow-up edits.\n"
                "\n## Coding Constraints (active during ALL coding phases)\n"
                "- Before writing ANY code, run `cat package.json` to check framework versions. If unsure, read official docs first.\n"
                "- Icons MUST come from Lucide/Heroicons/Tabler. No emoji as icons. No purple/pink gradient themes.\n"
                "- Frontend fetch URLs must exactly match backend route definitions.\n"
                "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
                "- After completing a feature, run build + lint. Fix errors before moving on.\n"
            )
            cursor_template = self.templates_dir / ".cursorrules.template"
            if cursor_template.exists():
                body = cursor_template.read_text(encoding="utf-8")
                rules_body = f"{body}\n\n{rules_body}"
            return (
                "---\n"
                'description: "Super Dev pipeline governance - research-first commercial-grade delivery. Activates when user says /super-dev or super-dev:"\n'
                "alwaysApply: true\n"
                "---\n\n"
                f"{rules_body}"
            )

        if target == "kiro" and relative.endswith("steering/super-dev.md"):
            frontmatter = (
                "---\n"
                "inclusion: always\n"
                "name: super-dev\n"
                "description: Super Dev pipeline governance for research-first commercial-grade delivery\n"
                "---\n\n"
            )
            return frontmatter + self._generic_ide_rules(target)

        if target == "antigravity":
            if relative.endswith(".agent/workflows/super-dev.md"):
                return self._antigravity_workflow_rules()
            return self._build_antigravity_context_content()

        if target in {
            "cursor",
            "windsurf",
            "cline",
            "continue",
            "vscode-copilot",
            "kilo-code",
            "roo-code",
            "augment",
            "qoder",
            "kiro",
            "trae",
            "codebuddy",
            "tongyi-lingma",
            "codegeex",
        }:
            return self._generic_ide_rules(target)

        if target in {
            "codex-cli",
            "copilot-cli",
            "opencode",
            "gemini-cli",
            "kiro-cli",
            "cursor-cli",
            "qoder-cli",
            "codebuddy-cli",
            "openclaw",
        }:
            return self._generic_cli_rules(target)

        if target == "claude-code":
            return self._claude_rules()

        return self._generic_cli_rules(target)

    def _build_codex_agents_content(self) -> str:
        return (
            "# Super Dev for Codex CLI\n\n"
            "When a user message starts with `super-dev:` or `super-dev：`, enter Super Dev pipeline mode immediately.\n\n"
            "If the repository already contains active Super Dev workflow context, the first natural-language requirement in a new session must also continue Super Dev rather than normal chat.\n\n"
            "## Direct Activation Rule\n"
            "- Do not spend a turn saying you will read the skill first, explain the skill, or decide whether to enter the workflow.\n"
            "- Treat the current trigger as already authorized to execute the full Super Dev pipeline.\n"
            "- If a compatibility skill under `~/.codex/skills/` is loaded, treat it as the same Super Dev contract, not a fallback mode.\n\n"
            "## Required execution\n"
            "1. First reply: state that Super Dev pipeline mode is active and the current phase is `research`.\n"
            "2. Read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` when available.\n"
            "3. Use Codex native web/search/edit/terminal capabilities to perform similar-product research and write `output/*-research.md` into the repository workspace.\n"
            "4. Draft `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` in the same Codex session and save them as actual project files.\n"
            "5. Stop after the three core documents, summarize them, and wait for explicit confirmation.\n"
            "6. Only after confirmation, create `.super-dev/changes/*/proposal.md` and `.super-dev/changes/*/tasks.md`, then continue with frontend-first implementation.\n\n"
            "## Constraints\n"
            "- Do not start coding directly after `super-dev:` or `super-dev：`.\n"
            "- Do not create Spec before document confirmation.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue.\n"
            "- 开始任何 UI 实现前，必须先锁定 `output/*-uiux.md` 中冻结的图标库、字体系统、design token system、组件生态和页面骨架。\n"
            "- Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- For non-conversational AI products, avoid Claude / ChatGPT-style sidebar chat shells unless the UI plan explicitly justifies them.\n"
            "- Keep using the component ecosystem and design token direction defined in `output/*-uiux.md` rather than switching ad hoc.\n"
            "- If a required artifact is only described in chat and not written into the repository, treat the step as incomplete.\n"
            "- Codex remains the execution host; Super Dev is the local governance workflow.\n"
            "- Use local `super-dev` CLI only for governance actions such as doctor, review, quality, release readiness, or update; do not outsource the main coding workflow to the CLI.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Super Dev System Flow Contract\n"
            "- SUPER_DEV_FLOW_CONTRACT_V1\n"
            "- PHASE_CHAIN: research>docs>docs_confirm>spec>frontend>preview_confirm>backend>quality>delivery\n"
            "- DOC_CONFIRM_GATE: required\n"
            "- PREVIEW_CONFIRM_GATE: required\n"
            "- HOST_PARITY: required\n"
        )

    def _build_claude_agent_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: Activate the Super Dev pipeline for research-first, commercial-grade project delivery. Use when user says /super-dev or super-dev: followed by a requirement.\n"
            "model: inherit\n"
            "---\n"
            "# Super Dev Core Subagent\n\n"
            "You are the Claude Code subagent that activates Super Dev governance mode.\n\n"
            "## Purpose\n"
            "- Treat `/super-dev ...` as the entry point into the Super Dev pipeline.\n"
            "- Enforce the sequence: research -> three core docs -> wait for confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- Use the local Python `super-dev` CLI for governance artifacts, checks, and delivery reports.\n"
            "- Use the host's native tools for browsing, coding, terminal execution, and debugging.\n\n"
            "## First Response Contract\n"
            "- On the first reply after `/super-dev ...`, explicitly say Super Dev pipeline mode is active.\n"
            "- If the repository already has active Super Dev workflow context, the first natural-language requirement in a new host session must also continue Super Dev rather than plain chat.\n"
            "- Explicitly say the current phase is `research`.\n"
            "- Explicitly state that you will read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` first when present.\n"
            "- Explicitly promise that you will stop after PRD, architecture, and UIUX for user confirmation before creating Spec or writing code.\n\n"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` as workspace files.\n"
            "- chat-only summaries do not count as completion.\n"
            "- If a required artifact is missing from the workspace, keep working until it is written.\n\n"
            "## Revision Contract\n"
            "- If the user requests UI changes, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime plus UI review.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, fix the issues first and rerun quality gate plus `super-dev release proof-pack` before continuing.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Implementation Closure Contract\n"
            "- After each code change, do a minimal diff review before claiming completion.\n"
            "- Run project-native build / compile / type-check / test / runtime smoke when available.\n"
            "- Ensure newly added functions, methods, fields, modules, and log hooks are wired into real call paths; delete them if unused.\n"
            "- Do not leave newly introduced unused code, dead branches, or helper functions that are only defined but never called.\n"
            "- Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- For non-conversational AI products, avoid Claude / ChatGPT-style chat shells unless the UI plan explicitly justifies them.\n"
            "- Keep using the design token direction and component ecosystem frozen in `output/*-uiux.md` rather than switching ad hoc.\n\n"
            "## Boundary\n"
            "- Claude Code remains the execution host.\n"
            "- Super Dev is the governance layer, not a separate model platform.\n"
            "- Prefer repository-local rules and commands as the source of project-specific context.\n"
        )

    def _build_codebuddy_agent_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: CodeBuddy subagent that activates the Super Dev pipeline for research-first, commercial-grade delivery.\n"
            "---\n"
            "# Super Dev Core Agent\n\n"
            "You are the CodeBuddy agent that activates Super Dev governance mode.\n\n"
            "## Purpose\n"
            "- Treat `/super-dev ...` as the entry point into the Super Dev pipeline.\n"
            "- Enforce the sequence: research -> three core docs -> wait for confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- Use the local Python `super-dev` CLI for governance artifacts, checks, and delivery reports.\n"
            "- Use CodeBuddy native tools for browsing, coding, terminal execution, and debugging.\n\n"
            "## First Response Contract\n"
            "- On the first reply after `/super-dev ...`, explicitly say Super Dev pipeline mode is active.\n"
            "- If the repository already has active Super Dev workflow context, the first natural-language requirement in a new host session must also continue Super Dev rather than plain chat.\n"
            "- Explicitly say the current phase is `research`.\n"
            "- Explicitly state that you will read `knowledge/` and `output/knowledge-cache/*-knowledge-bundle.json` first when present.\n"
            "- Explicitly promise that you will stop after PRD, architecture, and UIUX for user confirmation before creating Spec or writing code.\n\n"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` as real workspace files.\n"
            "- Do not treat chat-only explanations as completed deliverables.\n"
            "- If a required artifact is not present in the repository, continue until it is written.\n\n"
            "## Revision Contract\n"
            "- If the user requests UI changes, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime plus UI review.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign Spec/tasks and implementation.\n"
            "- If the user requests quality or security remediation, fix the issues first and rerun quality gate plus `super-dev release proof-pack` before continuing.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Implementation Closure Contract\n"
            "- After each code change, do a minimal diff review before claiming completion.\n"
            "- Run project-native build / compile / type-check / test / runtime smoke when available.\n"
            "- Ensure newly added functions, methods, fields, modules, and log hooks are wired into real call paths; delete them if unused.\n"
            "- Do not leave newly introduced unused code, dead branches, or helper functions that are only defined but never called.\n"
            "- Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- For non-conversational AI products, avoid Claude / ChatGPT-style chat shells unless the UI plan explicitly justifies them.\n"
            "- Keep using the design token direction and component ecosystem frozen in `output/*-uiux.md` rather than switching ad hoc.\n\n"
            "## Boundary\n"
            "- CodeBuddy remains the execution host.\n"
            "- Super Dev is the governance layer, not a separate model platform.\n"
            "- Prefer repository-local rules, commands, and this agent file as the source of project-specific context.\n"
        )

    def _build_embedded_skill_content(self) -> str:
        return (
            "---\n"
            "name: super-dev-core\n"
            "description: Super Dev pipeline governance for research-first, commercial-grade AI coding delivery\n"
            "---\n"
            "# super-dev-core - Super Dev AI Coding Skill\n\n"
            "## 定位边界（强制）\n"
            "- 当前宿主负责调用模型、工具、终端与实际代码修改。\n"
            "- Super Dev 不是大模型平台，也不提供自己的代码生成 API。\n"
            "- 你的职责是利用宿主现有能力，严格执行 Super Dev 的流程规范、设计约束、质量门禁与交付标准。\n\n"
            "## 触发方式（强制）\n"
            "- 支持 slash 的宿主：`/super-dev <需求描述>`。\n"
            "- 非 slash 宿主：`super-dev: <需求描述>` 与 `super-dev：<需求描述>` 等效。\n\n"
            "## 首轮响应契约（强制）\n"
            "- 第一轮回复必须明确说明当前阶段是 `research`。\n"
            "- 如果仓库里已经存在 Super Dev 上下文，新会话里的第一次自然语言需求也必须继续当前流程，而不是退回普通聊天。\n"
            "- 第一轮回复必须说明会先读取 `knowledge/` 与 `output/knowledge-cache/*-knowledge-bundle.json`。\n"
            "- 三份核心文档完成后会暂停等待用户确认；未经确认不得创建 `.super-dev/changes/*` 或开始编码。\n\n"
            "## 本地知识库契约（强制）\n"
            "- 先读 `knowledge/`。\n"
            "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取并把命中的本地知识带入三文档、Spec 与实现。\n"
            "- research、PRD、架构、UIUX、Spec、质量报告等要求中的产物，必须真实写入项目文件，不能只在聊天里口头描述。\n"
            "- 用户要求 UI 改版时，先更新 `output/*-uiux.md`，再重做前端并重新执行 frontend runtime 与 UI review。\n"
            "- 用户要求架构返工时，先更新 `output/*-architecture.md`，再同步调整 Spec / tasks 与实现方案。\n"
            "- 用户要求质量整改时，先修复问题，再重新执行 quality gate 与 `super-dev release proof-pack`。\n"
            "- 若当前项目启用了 policy / 强治理策略，不得默认建议关闭红队、降低质量阈值或跳过门禁；只有在用户明确要求降级治理强度时，才可说明风险后调整 policy。\n"
            "- 完成每轮代码修改后，必须先做一次最小 diff review，再汇报“已完成”。\n"
            "- 必须运行项目原生 build / compile / type-check / test / runtime smoke；若不存在某项，要说明原因。\n"
            "- 本轮新增函数、方法、字段、模块、日志埋点必须接入真实调用链；未接入则删除，不允许只定义不使用。\n"
            "- 不允许留下新增 unused code、只定义不调用的 helper、无效日志或无效兜底分支。\n\n"
            "## 会话连续性契约（强制）\n"
            "- 若存在 `.super-dev/SESSION_BRIEF.md`，每次继续前必须先读取，并把它视为当前流程状态真源。\n"
            "- 当前流程停在确认门或返工门时，用户说“改一下”“补充”“继续改”“确认”“通过”“继续”等，都属于当前流程内动作，不得退回普通聊天。\n"
            "- 每次按用户意见修改后，必须留在当前门里，重新总结变化，并再次等待明确确认。\n"
            "- 只有用户明确说取消当前流程、重新开始、或切回普通聊天时，才允许离开当前 Super Dev 流程。\n\n"
        )

    def _build_slash_command_content(self, target: str) -> str:
        if target == "windsurf":
            return (
                "---\n"
                "description: Super Dev 流水线式开发编排（先文档/Spec，再编码）\n"
                "---\n\n"
                "# /super-dev (windsurf)\n\n"
                "在当前项目触发 Super Dev 流水线。\n\n"
                "## 输入\n"
                "- 需求描述: `$ARGUMENTS`\n\n"
                "## 定位边界\n"
                "- 宿主负责调用自身模型、工具与实际编码。\n"
                "- Super Dev 负责流程规范、质量门禁、审计产物与交付标准。\n\n"
                "## 本地知识库要求\n"
                "- 先读取当前项目 `knowledge/` 下与需求相关的知识文件。\n"
                "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取其中的 `local_knowledge`、`web_knowledge` 与 `research_summary`。\n"
                "- 命中的本地知识应被继承到 PRD / 架构 / UIUX / Spec，而不是只停留在 research 文档。\n\n"
                "## 强制执行顺序\n"
                "1. 先使用宿主原生联网 / browse / search 研究同类产品，沉淀 `output/*-research.md`\n"
                "2. 再生成 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`\n"
                "3. 三份文档完成后，先向用户汇报文档摘要与路径，等待明确确认；未经确认不得创建 Spec 或开始编码\n"
                "4. 用户确认后，再生成 `.super-dev/changes/*/proposal.md` 与 `tasks.md`\n"
                "5. 先实现并运行前端，再进入后端、联调、测试与交付\n\n"
                "## 研究要求\n"
                "- 至少研究 3 到 5 个可借鉴产品\n"
                "- 总结共性功能、关键交互、信息架构、商业表达与差异化方向\n"
                "- 未完成 research 阶段前不得直接进入编码\n\n"
                "## 执行命令\n"
                "```bash\n"
                "super-dev create \"$ARGUMENTS\"\n"
                "super-dev spec list\n"
                "```\n"
            )

        if target == "kiro":
            return (
                "---\n"
                "inclusion: manual\n"
                "---\n\n"
                "# super-dev\n\n"
                "在 Kiro 手动触发 `/super-dev` 时执行以下流程：\n\n"
                "定位边界：宿主负责编码与工具调用，Super Dev 负责流程和质量治理。\n\n"
                "本地知识库要求：\n"
                "- 先读取当前项目 `knowledge/` 下与需求相关的知识文件\n"
                "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须先读取其中命中的本地知识与研究摘要\n"
                "- 命中的规范、清单、反模式默认视为项目硬约束\n\n"
                "1. 先使用宿主原生联网 / browse / search 研究同类产品，沉淀 `output/*-research.md`\n"
                "2. 再生成 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`\n"
                "3. 三份文档完成后，先停下来向用户汇报并等待确认；未经确认不得创建 Spec 或开始编码\n"
                "4. 用户确认后，再创建 `.super-dev/changes/*/proposal.md` 与 `tasks.md`\n"
                "5. 先实现并运行前端，再进入后端、联调、测试与交付\n\n"
                "研究阶段至少输出：同类产品名单、共性功能、关键页面结构、交互模式、差异化建议。\n\n"
                "执行命令：\n"
                "```bash\n"
                "super-dev create \"$ARGUMENTS\"\n"
                "super-dev spec list\n"
                "```\n"
            )

        return (
            f"# /super-dev ({target})\n\n"
            "在当前项目触发 Super Dev 的流水线式开发编排。\n\n"
            "## 输入\n"
            "- 需求描述: `$ARGUMENTS`\n"
            "- 如果未提供参数，先要求用户补全需求后再执行。\n\n"
            "## Super Dev Runtime Contract\n"
            "- Super Dev 是当前项目里的本地 Python 工具 + 宿主规则/Skill 协议，不是独立模型平台。\n"
            "- 宿主负责推理、联网、编码、运行终端与修改文件。\n"
            "- 当用户触发 `/super-dev` 时，你要把它视为“进入 Super Dev 流水线”，而不是普通聊天命令。\n"
            "- 需要生成文档、Spec、质量报告、交付产物时，优先调用本地 `super-dev` CLI。\n"
            "- 需要研究、设计、编码、运行、修复时，优先使用宿主自身的 browse/search/terminal/edit 能力。\n\n"
            "## Local Knowledge Contract\n"
            "- 优先读取当前项目 `knowledge/` 目录里与需求相关的知识文件。\n"
            "- 若存在 `output/knowledge-cache/*-knowledge-bundle.json`，必须读取其中命中的 `local_knowledge`、`web_knowledge` 与 `research_summary`。\n"
            "- 本地知识命中的规范、检查清单、反模式、场景包默认是当前项目的硬约束，后续三文档、Spec 与实现都要继承。\n\n"
            f"{self._first_response_contract_zh()}"
            "## 强制执行顺序（不可跳步）\n"
            "1. 先使用宿主原生联网 / browse / search 能力研究同类产品，并先产出：\n"
            "   - `output/*-research.md`\n"
            "   - 至少包含 3-5 个对标产品、共性功能、关键流程、信息架构、交互模式、差异化方向\n"
            "2. 再生成三份核心文档，再进入编码阶段：\n"
            "   - `output/*-prd.md`\n"
            "   - `output/*-architecture.md`\n"
            "   - `output/*-uiux.md`\n"
            "3. 三份核心文档完成后，必须先暂停并向用户汇报文档路径、摘要与待确认事项；未经用户明确确认，不得进入 Spec 或编码。\n"
            "4. 用户确认后，再创建 Spec 变更与任务清单：\n"
            "   - `.super-dev/changes/*/proposal.md`\n"
            "   - `.super-dev/changes/*/tasks.md`\n"
            "5. 先按 `tasks.md` 实现并运行前端，确保前端可演示、可审查、无明显错误。\n"
            "6. 再实现后端、联调、测试、质量门禁与可审计交付清单。\n\n"
            "## 执行命令（优先）\n"
            "```bash\n"
            "super-dev create \"$ARGUMENTS\"\n"
            "super-dev spec list\n"
            "```\n\n"
            "## 实现阶段要求\n"
            "- 如果宿主具备联网能力，必须优先在宿主中完成同类产品研究，不能跳过 research 阶段直接编码。\n"
            "- 研究结论必须回填到 `output/*-research.md`，并用于约束 PRD / 架构 / UIUX。\n"
            "- 编码前必须先读取 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`，并完成用户确认门。\n"
            "- 如果用户要求修改文档，只允许回到文档阶段修订，不能绕过确认门直接建 Spec 或开工。\n"
            "- UI 必须遵循 UI/UX 文档，禁止直接输出模板化、同质化页面。\n"
            "- 默认避免宿主自动滑向“AI 感”设计：紫/粉渐变主视觉、emoji 充当功能图标、默认系统字体直出；只有用户或品牌明确要求时才可采用，并写清理由。\n"
            "- 开始任何 UI 实现前，必须先声明图标库；功能图标只能来自 Lucide / Heroicons / Tabler / 官方组件图标。\n"
            "- 非对话式 AI 产品默认避免复刻 Claude / ChatGPT 式侧栏聊天壳层、窄中栏对话布局和同款中性色配色；若业务确实需要则必须写明适配理由。\n"
            "- 编码前必须先明确视觉方向、字体系统、颜色 token、间距 token、栅格系统、组件状态矩阵。\n"
            "- 页面必须提供可访问交互：可见 `focus` 态、合理 hover/active、兼容 reduced-motion。\n"
            "- 严禁在三文档与 Spec 缺失时直接宣称“已完成”。\n\n"
            "## 汇报格式（每次回复都要包含）\n"
            "- 当前阶段（文档 / Spec / 实现 / 质量 / 交付）\n"
            "- 本次变更文件路径\n"
            "- 下一步动作\n\n"
            "## 说明\n"
            "- 宿主负责调用自身模型、工具与实际编码；Super Dev 只提供治理协议。\n"
            "- Super Dev 不提供模型能力；编码能力来自当前宿主。\n"
            "- 在宿主会话中执行本流程，确保上下文连续与结果可审计。\n"
        )

    def _generic_cli_rules(self, target: str) -> str:
        if self.supports_slash(target):
            trigger_lines = (
                "## Trigger\n"
                '- Preferred: `/super-dev "<需求描述>"`\n'
                '- Terminal entry (local orchestration only): `super-dev "<需求描述>"`\n'
                "- Terminal entry does not directly talk to the host model session.\n\n"
            )
        else:
            trigger_lines = (
                "## Trigger\n"
                '- Preferred: say `super-dev: <需求描述>` or `super-dev：<需求描述>` in the host chat so AGENTS.md + super-dev-core Skill can govern the workflow.\n'
                '- Local orchestration fallback: `super-dev "<需求描述>"`\n'
                "- Do not rely on `/super-dev` in this host.\n\n"
            )
        return (
            f"# Super Dev Integration for {target}\n\n"
            "Super Dev 是“超级开发战队”，一个流水线式 AI Coding 辅助工具。\n"
            "Super Dev does not provide model inference or coding APIs.\n"
            "The host remains responsible for model execution, tools, and actual code generation.\n"
            "Use the host model/runtime as-is; Super Dev only enforces the delivery protocol.\n"
            "Use Super Dev generated artifacts as source of truth.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as a local Python CLI plus host-side rules/skills, not as a separate model provider.\n"
            "- When the user triggers Super Dev, enter the protocol immediately instead of treating it as normal chat.\n"
            "- Use host-native web/search/browse for research and host-native editing/execution for implementation.\n"
            "- Use local `super-dev` commands to generate/update documents, spec artifacts, quality reports, and delivery outputs.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read its `local_knowledge`, `web_knowledge`, and `research_summary` first.\n"
            "- Treat matched local knowledge, checklists, anti-patterns, and scenario packs as project constraints that must flow into docs, spec, and implementation.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            f"{trigger_lines}"
            "## Required Context\n"
            "- output/*-prd.md\n"
            "- output/*-architecture.md\n"
            "- output/*-uiux.md\n"
            "- output/*-execution-plan.md\n"
            "- .super-dev/changes/*/tasks.md\n\n"
            "## Execution Order\n"
            "1. Use the host's native browse/search/web capability to research similar products first and produce output/*-research.md as a real repository file\n"
            "2. Freeze PRD, architecture and UIUX documents and write them into output/* files in the repository workspace rather than only describing them in chat\n"
            "3. Stop after the three core documents, summarize them to the user, and wait for explicit confirmation before creating Spec or coding\n"
            "4. Create Spec proposal/tasks only after the user confirms the documents\n"
            "5. Implement and run the frontend first so it becomes demonstrable before backend-heavy work\n"
            "6. Implement backend APIs and data layer, then run tests, quality gate, and release preparation\n"
            "7. If the user says the UI is unsatisfactory, asks for a redesign, or says the page looks AI-generated, first update `output/*-uiux.md`, then redo frontend implementation, rerun frontend runtime and UI review, and only then continue.\n"
            "8. If the user says the architecture is wrong or the technical plan must change, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "9. If the user says quality or security is not acceptable, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue.\n"
            "10. Before any UI implementation, first lock the icon library, typography, token system, component ecosystem, and page skeleton according to `output/*-uiux.md`.\n"
            "11. Do not use emoji as functional icons or placeholders, and do not leave icon decisions for later.\n"
            "12. For non-conversational AI products, default to avoiding Claude / ChatGPT-style sidebar chat shells, narrow-center conversation layouts, and the same neutral chat color shell unless the UI plan explicitly justifies it.\n"
            "13. UI implementation must use the recommended component ecosystem/design token direction from `output/*-uiux.md`, not switch ad hoc.\n"
            "\n\n## Coding Constraints (active during ALL coding phases)\n\n"
            "These rules apply every time you write or edit a file:\n\n"
            "### Tech Stack Pre-Research\n"
            "- Before writing ANY code, run `cat package.json` (or equivalent) to check framework versions.\n"
            "- If unsure about an API, use WebFetch to read official docs first. Never guess.\n\n"
            "### Icon & Visual Rules\n"
            "- Icons MUST come from a declared icon library (Lucide/Heroicons/Tabler). No emoji as icons.\n"
            "- No purple/pink gradient themes. No default system font only.\n\n"
            "### Frontend/Backend Alignment\n"
            "- Frontend fetch URLs must exactly match backend route definitions.\n"
            "- Define API paths as shared constants when possible.\n\n"
            "### Per-File Self-Check\n"
            "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
            "- After completing a feature, run build + lint. Fix errors before moving on.\n"
        )

    def _generic_ide_rules(self, target: str) -> str:
        windsurf_frontmatter = ""
        if target == "windsurf":
            windsurf_frontmatter = (
                "---\n"
                "trigger: always_on\n"
                "---\n\n"
            )
        return (
            f"{windsurf_frontmatter}"
            f"# Super Dev IDE Rules ({target})\n\n"
            "## Positioning\n"
            "- Super Dev is a host-level workflow governor, not an LLM platform.\n"
            "- Keep using the host's model capabilities; do not expect extra model APIs from Super Dev.\n"
            "- The host remains responsible for actual coding, tool execution, and file changes.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus this host rule file, not as a separate coding engine.\n"
            "- When the user says `/super-dev ...`, `super-dev: ...`, or `super-dev：...`, immediately enter the Super Dev pipeline.\n"
            "- Use host-native browse/search/web for research and host-native editing/terminal for implementation.\n"
            "- Use local `super-dev` commands when you need to generate or refresh documents, spec artifacts, quality reports, or delivery manifests.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting the three core documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its matched local knowledge into PRD, architecture, UIUX, Spec, and execution.\n"
            "- Treat local knowledge hits as hard project constraints, especially for standards, anti-patterns, checklists, and scenario packs.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Working Agreement\n"
            "- If the host supports browse/search/web, research similar products first and write the findings into output/*-research.md.\n"
            "- Generate PRD, architecture and UIUX documents before coding, write them into output/* files, then pause and ask the user to confirm the three documents.\n"
            "- If the user requests revisions, update the documents first and ask again; do not create Spec or code before confirmation.\n"
            "- If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate plus `super-dev release proof-pack`, and only then continue.\n"
            "- Respect Spec tasks sequence.\n"
            "- Implement and run the frontend before moving into backend-heavy work.\n"
            "- Keep architecture and UIUX consistency.\n\n"
            "## Delivery Criteria\n"
            "- Frontend can be demonstrated early.\n"
            "- Backend and migration scripts match specs.\n"
            "- Security/performance checks are resolved.\n"
            "- Quality gate threshold is met for the current scenario.\n"
            "- UI must avoid AI-looking output (purple/pink gradient-first theme, emoji as icons, default-font-only pages).\n"
            "- Before any UI implementation, lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- For non-conversational AI products, avoid Claude / ChatGPT-style sidebar chat shells unless the UI plan explicitly justifies it.\n"
            "- UI must define typography, design tokens, grid, component states and trust signals before page implementation.\n"
            "- Prefer the component ecosystem and design token baseline recommended in output/*-uiux.md instead of switching UI libraries ad hoc.\n"
            "\n\n## Coding Constraints (active during ALL coding phases)\n\n"
            "These rules apply every time you write or edit a file:\n\n"
            "### Tech Stack Pre-Research\n"
            "- Before writing ANY code, run `cat package.json` (or equivalent) to check framework versions.\n"
            "- If unsure about an API, use WebFetch to read official docs first. Never guess.\n\n"
            "### Icon & Visual Rules\n"
            "- Icons MUST come from a declared icon library (Lucide/Heroicons/Tabler). No emoji as icons.\n"
            "- No purple/pink gradient themes. No default system font only.\n\n"
            "### Frontend/Backend Alignment\n"
            "- Frontend fetch URLs must exactly match backend route definitions.\n"
            "- Define API paths as shared constants when possible.\n\n"
            "### Per-File Self-Check\n"
            "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
            "- After completing a feature, run build + lint. Fix errors before moving on.\n"
        )

    def _trae_rules(self) -> str:
        return (
            "# Super Dev Trae Rules\n\n"
            "## Critical Trigger Switch\n"
            "- If a user message starts with `super-dev:` or `super-dev：`, immediately switch into Super Dev pipeline mode.\n"
            "- If the repository already has active Super Dev workflow context, the first natural-language requirement in a new session must also continue Super Dev.\n"
            "- Do not treat `super-dev:` or `super-dev：` as normal chat, brainstorming, or generic coding mode.\n"
            "- After `super-dev:` or `super-dev：` is seen, do not start implementation directly.\n"
            "- Your first reply must say `SMOKE_OK` when the user is smoke-testing, or explicitly say Super Dev pipeline mode is active.\n"
            "- Your first reply must explicitly say the current phase is `research`.\n"
            "- Your first reply must explicitly promise the sequence: research -> three core documents -> wait for user confirmation -> Spec/tasks -> frontend runtime verification -> backend/tests/delivery.\n"
            "- After the three core documents are generated, you must stop and wait for approval before creating Spec or writing code.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus Trae rule files, not as a separate coding engine.\n"
            "- Keep using the host's model, tools, browse/search/web and editor capabilities.\n"
            "- Use local `super-dev` commands when you need to generate or refresh documents, specs, quality reports, or delivery manifests.\n"
            "- The host remains responsible for coding, tool execution, and file changes.\n\n"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting the three core documents.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and carry its matched local knowledge into PRD, architecture, UIUX, Spec, and execution.\n"
            "- Treat matched standards, anti-patterns, checklists, baselines, and scenario packs as hard constraints.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Working Agreement\n"
            "- If browse/search/web is available, research similar products first and write `output/*-research.md` into the project workspace.\n"
            "- Generate PRD, architecture, and UIUX before coding and save them as `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` instead of only replying in chat.\n"
            "- Ask the user to confirm or revise the three documents before creating Spec or code.\n"
            "- If a document is mentioned in chat but not written to the repository, treat the step as incomplete and keep working until the file exists.\n"
            "- If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n"
            "- If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation before continuing.\n"
            "- If the user requests quality or security remediation, first fix the issues, rerun quality gate plus `super-dev release proof-pack`, and only then continue.\n"
            "- Implement frontend first and verify runtime before moving into backend-heavy work.\n"
            "- Keep UI implementation consistent with `output/*-uiux.md` and avoid AI-looking templates.\n"
            "- Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- Keep using the design token direction and component ecosystem frozen in `output/*-uiux.md` rather than switching ad hoc.\n"
            "\n\n## Coding Constraints (active during ALL coding phases)\n\n"
            "These rules apply every time you write or edit a file:\n\n"
            "### Tech Stack Pre-Research\n"
            "- Before writing ANY code, run `cat package.json` (or equivalent) to check framework versions.\n"
            "- If unsure about an API, use WebFetch to read official docs first. Never guess.\n\n"
            "### Icon & Visual Rules\n"
            "- Icons MUST come from a declared icon library (Lucide/Heroicons/Tabler). No emoji as icons.\n"
            "- No purple/pink gradient themes. No default system font only.\n\n"
            "### Frontend/Backend Alignment\n"
            "- Frontend fetch URLs must exactly match backend route definitions.\n"
            "- Define API paths as shared constants when possible.\n\n"
            "### Per-File Self-Check\n"
            "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
            "- After completing a feature, run build + lint. Fix errors before moving on.\n"
        )

    def _claude_rules(self) -> str:
        return (
            "# Super Dev Claude Code Integration\n\n"
            "This project uses a pipeline-driven development model.\n\n"
            "## Positioning\n"
            "- Super Dev does not own a model endpoint.\n"
            "- Claude Code remains the execution host for coding capability.\n"
            "- Super Dev provides governance: protocol, gates, and audit artifacts.\n\n"
            "## Runtime Contract\n"
            "- Treat Super Dev as the local Python workflow tool plus Claude Code command/rule integration.\n"
            "- When the user triggers `/super-dev`, `super-dev:`, or `super-dev：`, enter the Super Dev pipeline immediately rather than handling it like casual chat.\n"
            "- Use Claude Code browse/search for research and Claude Code terminal/editing for implementation.\n"
            "- Use local `super-dev` commands whenever you need to generate/update docs, spec artifacts, quality reports, and delivery outputs.\n\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read relevant files under `knowledge/` before drafting PRD, architecture, and UIUX.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, read it first and inherit its local knowledge hits into later stages.\n"
            "- Treat matched local standards, scenario packs, and checklists as hard constraints, not optional hints.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Before coding\n"
            "1. If Claude Code browse/search is available, research similar products first and write output/*-research.md as a real repository file\n"
            "2. Read output/*-prd.md\n"
            "3. Read output/*-architecture.md\n"
            "4. Read output/*-uiux.md\n"
            "5. Summarize the three core documents to the user and wait for explicit confirmation before creating Spec or coding\n"
            "6. Chat-only summaries do not count as completion; the required artifacts must exist in the workspace\n"
            "7. Read output/*-execution-plan.md\n"
            "8. Follow .super-dev/changes/*/tasks.md after confirmation, with frontend-first implementation and runtime verification\n\n"
            "9. If the user requests a UI redesign or says the UI is unsatisfactory, first update `output/*-uiux.md`, then redo the frontend, and rerun frontend runtime + UI review before continuing.\n\n"
            "## Output Quality\n"
            "- Keep security/performance constraints from red-team report.\n"
            "- Ensure quality gate threshold is met before merge.\n"
            "- UI must follow output/*-uiux.md and avoid AI-looking templates (purple gradient, emoji icons, default-font-only).\n"
            "- Before any UI implementation, lock the icon library, typography, design token system, component ecosystem, and page skeleton from output/*-uiux.md.\n"
            "- Do not use emoji as functional icons or placeholders.\n"
            "- For non-conversational AI products, avoid Claude / ChatGPT-style shells unless the UI plan explicitly justifies them.\n"
            "- UI implementation must define typography system, design tokens, page hierarchy and component states before polishing visuals.\n"
            "- Prioritize real screenshots, trust modules, proof points and task flows over decorative hero sections.\n\n"
            "## Coding Constraints (active during ALL coding phases)\n\n"
            "These rules apply every time you write or edit a file. They are NOT suggestions:\n\n"
            "### Tech Stack Pre-Research\n"
            "- Before writing ANY code, run `cat package.json` (or equivalent) to check framework versions.\n"
            "- If unsure about an API for the installed version, use WebFetch to read official docs first.\n"
            "- Never guess API signatures. Check docs.\n\n"
            "### Icon & Visual Rules\n"
            "- Icons MUST come from a declared icon library (Lucide/Heroicons/Tabler). No emoji as icons.\n"
            "- No purple/pink gradient themes. No default system font only.\n"
            "- Before showing any UI code, self-check: no emoji characters in the source.\n\n"
            "### Frontend/Backend Alignment\n"
            "- Frontend fetch URLs must exactly match backend route definitions.\n"
            "- Define API paths as shared constants when possible.\n\n"
            "### Per-File Self-Check\n"
            "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
            "- After completing a feature, run build + lint. Fix errors before moving on.\n\n"
            "### CLI Commands During Coding\n"
            "- Run `super-dev enforce validate` after writing UI code.\n"
            "- Run `super-dev quality` after completing a feature.\n"
            "- Run `super-dev review --state ui` after frontend is done.\n"
            "- Run `super-dev release proof-pack` before final delivery.\n\n"
            "## Three-Layer Governance Model\n\n"
            "Super Dev governance operates at three layers:\n\n"
            "**Layer 1 — CLAUDE.md (Persistent Rules)**\n"
            "These rules are ALWAYS in context. They override default behavior.\n\n"
            "**Layer 2 — Hooks (Runtime Enforcement)**\n"
            "PreToolUse hooks validate every file write. PostToolUse hooks audit results.\n"
            "Hooks are auto-registered when /super-dev is invoked.\n\n"
            "**Layer 3 — CLI Commands (On-Demand Checks)**\n"
            "Run `super-dev enforce validate` / `super-dev quality` for deeper checks.\n"
            "These are triggered at key milestones, not every turn.\n"
        )

    def _antigravity_workflow_rules(self) -> str:
        """
        生成 Antigravity IDE 专属工作流配置。
        文件写入 .agent/workflows/super-dev.md，
        格式遵循 Antigravity Skill YAML frontmatter + markdown 规范。
        """
        return """\
---
description: Super Dev 流水线式 AI Coding 辅助工作流 - 从需求到交付的 12 阶段自动化流程
---

# Super Dev Pipeline Workflow

## 角色定义

本工作流激活 11 位专家角色自动协作：

| 专家 | 职责 |
|:---|:---|
| PRODUCT | 首次上手、产品闭环、功能缺口与优先级总审查 |
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

### 第 0 阶段：需求增强与同类产品研究

```bash
super-dev "你的需求描述"
```

- 解析自然语言需求，注入领域知识库
- 优先使用宿主原生联网能力研究同类产品、关键流程、页面结构和交互模式
- 联网检索补充市场和技术背景
- 输出 `output/*-research.md`，沉淀对标结论、共性功能和差异化机会
- 输出结构化需求蓝图

### 第 1 阶段：专业文档生成

自动生成：
- `output/*-prd.md` — PRD（产品需求文档）
- `output/*-architecture.md` — 架构设计文档
- `output/*-uiux.md` — UI/UX 设计文档
- 以上产物必须真实写入项目工作区；只在聊天里总结不算完成

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

- 进入 Super Dev 流程后，第一轮必须明确当前阶段是 `research`
- 三份核心文档完成后，必须暂停等待用户确认
- 未经用户确认，不得创建 `.super-dev/changes/*` 或开始编码
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

    def _build_antigravity_context_content(self) -> str:
        return (
            "# Super Dev Antigravity Context\n\n"
            "Antigravity remains the execution host for model reasoning, browsing, terminal work, and code changes.\n"
            "Super Dev is the governance layer and local Python toolchain.\n\n"
            "## Trigger\n"
            "- Preferred: `/super-dev \"<需求描述>\"`\n"
            "- Fallback in local terminal only: `super-dev \"<需求描述>\"`\n"
            "- The terminal fallback does not replace the Antigravity host session.\n\n"
            "## Required First Response Contract\n"
            f"{self._first_response_contract_en()}"
            "## Local Knowledge Contract\n"
            "- Read `knowledge/` first when relevant.\n"
            "- If `output/knowledge-cache/*-knowledge-bundle.json` exists, inherit its local knowledge hits into research, PRD, architecture, UIUX, Spec, and implementation.\n\n"
            f"{self._conversation_continuity_contract_en()}"
            "## Artifact Contract\n"
            "- Write `output/*-research.md`, `output/*-prd.md`, `output/*-architecture.md`, and `output/*-uiux.md` into the repository workspace.\n"
            "- Chat-only summaries do not count as finished artifacts.\n"
            "- If a required artifact is missing from the workspace, continue until it exists.\n\n"
            "## Required Execution Order\n"
            "1. Research similar products first using host-native browse/search and write `output/*-research.md`\n"
            "2. Generate PRD, architecture, and UIUX and write them as project files\n"
            "3. Stop and wait for explicit user confirmation before Spec or coding\n"
            "4. Create Spec/tasks only after confirmation\n"
            "5. Implement and run the frontend first\n"
            "6. Continue with backend, tests, quality gate, and delivery\n"
            "7. If the user requests a UI redesign, first update `output/*-uiux.md`, then redo the frontend and rerun frontend runtime + UI review\n"
            "8. If the user requests architecture changes, first update `output/*-architecture.md`, then realign tasks and implementation\n"
            "9. If the user requests quality remediation, first fix the issues, rerun quality gate and `super-dev release proof-pack`, and only then continue\n"
            "10. Before any UI implementation, first lock the icon library, typography, design token system, component ecosystem, and page skeleton from `output/*-uiux.md`\n"
            "11. Do not use emoji as functional icons or placeholders\n"
            "12. Keep using the design token direction and component ecosystem frozen in `output/*-uiux.md` rather than switching ad hoc\n\n"
            "## Coding Constraints (active during ALL coding phases)\n\n"
            "- Before writing ANY code, run `cat package.json` to check framework versions. If unsure, read official docs first.\n"
            "- Icons MUST come from Lucide/Heroicons/Tabler. No emoji as icons. No purple/pink gradient themes.\n"
            "- Frontend fetch URLs must exactly match backend route definitions.\n"
            "- Before writing each file: correct imports, no emoji, colors from tokens only.\n"
            "- After completing a feature, run build + lint. Fix errors before moving on.\n"
        )
