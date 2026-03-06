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
        "opencode": "~/.config/opencode/skills",
        "qoder-cli": "~/.qoder/skills",
        "qoder": "~/.qoderwork/skills",
        "windsurf": "~/.codeium/windsurf/skills",
    }

    # Observed compatibility paths used when a host exposes a local skill loader
    # but the vendor docs do not yet publish a stable user-level install path.
    OBSERVED_TARGET_PATHS = {
        "claude-code": "~/.claude/skills",
        "cursor-cli": "~/.cursor/skills",
        "cursor": "~/.cursor/skills",
        "gemini-cli": "~/.gemini/skills",
        "kimi-cli": "~/.kimi/skills",
        "kiro-cli": "~/.kiro/skills",
        "kiro": "~/.kiro/skills",
        "trae": "~/.trae/skills",
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
            self._write_builtin_skill(target_dir, skill_name)
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

    def _write_builtin_skill(self, target_dir: Path, skill_name: str) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        skill_content = f"""---
name: {skill_name}
description: Super Dev pipeline governance for research-first, commercial-grade AI coding delivery
---
# {skill_name} - Super Dev AI Coding Skill

> 版本: 2.0.8 | 适用工具: Claude Code, Codex CLI, OpenCode, Cursor, Antigravity 等所有 AI Coding 工具

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
- 不支持 `/super-dev` 的宿主：把 `super-dev: <需求描述>` 视为等效触发词。
- 当用户使用这个文本触发词时，立即进入完整的 Super Dev 流水线，而不是把它当作普通聊天内容。

## Runtime Contract（强制）

- Super Dev 由两部分组成：
  1. 当前项目内的本地 Python CLI 工具
  2. 当前宿主里的规则/Skill/命令映射
- 当前宿主负责调用模型、联网、终端、编辑器与实际代码修改。
- 当用户触发 `/super-dev ...` 或 `super-dev: ...` 时，意味着你必须进入 Super Dev 流水线。
- 需要生成或刷新文档、Spec、质量报告、交付产物时，优先调用本地 `super-dev` CLI。
- 需要研究、设计、编码、运行、调试时，优先使用宿主自身的 browse/search/terminal/edit 能力。
- 不要等待用户解释“Super Dev 是什么”；你要把它理解为当前项目已经安装好的开发治理协议。

## 首轮响应契约（强制）

- 当用户首次输入 `/super-dev <需求描述>` 或 `super-dev: <需求描述>` 时，第一轮回复必须明确说明：Super Dev 流水线已激活，当前不是普通聊天模式。
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

| 专家角色 | 触发场景 | 核心职责 |
|:---|:---|:---|
| **PM（产品经理）** | 需求分析、PRD 生成 | 需求拆解、用户故事、验收标准 |
| **ARCHITECT（架构师）** | 系统设计、技术选型 | 架构图、技术栈选型、API 契约 |
| **UI（UI 设计师）** | 视觉设计、组件规范 | 设计系统、色彩规范、组件库 |
| **UX（UX 设计师）** | 交互设计、用户体验 | 用户旅程、信息架构、可用性 |
| **SECURITY（安全专家）** | 红队审查、漏洞检测 | OWASP Top 10、威胁建模 |
| **CODE（代码专家）** | 代码实现、最佳实践 | 设计模式、代码审查、重构 |
| **DBA（数据库专家）** | 数据库设计、优化 | 表结构、索引策略、迁移脚本 |
| **QA（质量保证）** | 测试策略、质量门禁 | 测试计划、覆盖率、质量评分 |
| **DEVOPS（运维工程师）** | CI/CD、部署配置 | 流水线、容器化、监控告警 |
| **RCA（根因分析）** | 故障复盘、风险识别 | 根因分析、改进建议、预防措施 |

---

## 12 阶段开发流水线

接到任务后，**严格按以下顺序执行**：

```
第 0 阶段  同类产品研究 → 优先使用宿主原生联网能力，研究相似产品、关键流程、页面结构、交互模式
第 1 阶段  需求增强    → 解析需求 + 注入知识库 + 研究结论结构化
第 2 阶段  文档生成    → PRD + 架构设计 + UI/UX 文档
第 3 阶段  文档确认门  → 汇报三文档并等待用户确认；未确认不得进入 Spec 或编码
第 4 阶段  Spec 创建   → 结构化规范 + 任务列表
第 5 阶段  前端骨架    → 先交付可演示前端并实际运行验证
第 6 阶段  后端实现    → API / 数据层 / 认证 / 联调
第 7 阶段  红队审查    → 安全 + 性能 + 架构三维审查
第 8 阶段  质量门禁    → 统一阈值（80+）
第 9 阶段  代码审查    → 生成代码审查指南
第 10 阶段 CI/CD       → 5 大平台配置（GitHub/GitLab/Jenkins/Azure/Bitbucket）
第 11 阶段 部署修复模板 → 环境变量示例 + 平台检查清单
第 12 阶段 交付收敛    → 迁移脚本 + 交付包（manifest/report/zip）
```

---

## 同类产品研究规则（强制）

在任何文档生成前，先用宿主原生联网 / browse / search 能力完成研究，并写入 `output/*-research.md`：

1. 至少研究 3 到 5 个同类产品或相近解决方案
2. 总结它们的：
   - 共性功能
   - 关键用户路径
   - 页面信息架构
   - 交互模式
   - 信任表达与商业化表达
   - 不应该照搬的缺点
3. 明确本项目的差异化方向
4. 未完成 research 阶段前，禁止直接进入编码

---

## 文档确认门（强制）

当 `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md` 三份核心文档生成后，必须立刻执行以下步骤：

1. 向用户汇报三份文档的路径与核心结论
2. 明确要求用户给出“确认进入下一阶段”或“提出修改意见”
3. 如果用户要求修改，只允许先修正文档并再次汇报
4. **未经用户明确确认，禁止创建 `.super-dev/changes/*`，禁止开始前端，禁止开始后端，禁止声称进入实现阶段**

---

## 开始前必读（强制）

**在写任何一行代码之前**，必须先读取以下文档：

1. `output/*-research.md` — 同类产品研究与结论
2. `output/*-prd.md` — 产品需求文档（功能边界、验收标准）
3. `output/*-architecture.md` — 架构设计文档（技术栈、API 规范）
4. `output/*-uiux.md` — UI/UX 设计文档（设计系统、组件规范）
5. `output/*-execution-plan.md` — 执行路线图（阶段任务和里程碑）
6. `.super-dev/changes/*/tasks.md` — Spec 任务列表（逐项实现）

---

## 商业级 UI/UX 规则（强制）

UI 相关工作不能直接“开始画页面”，必须先完成设计系统定义：

1. 先确定视觉方向：品牌气质、信息层级、页面密度
2. 先确定字体系统：标题字体、正文字体、字号层级、字重节奏
3. 先确定设计 token：颜色、间距、圆角、阴影、边框、动效时长
4. 先确定布局规则：栅格、容器宽度、页面分区、桌面与移动端密度
5. 先确定组件状态矩阵：默认、hover、active、focus、loading、empty、error、disabled
6. 先明确商业化与信任元素：案例、数据证明、权限反馈、风险提示、空态/错误态
7. 优先采用 `output/*-uiux.md` 中推荐的组件生态和实现基线，不要临时切换到另一套 UI 库

同时严格遵守：

- 禁止紫色/粉色渐变主视觉作为默认输出，除非品牌明确要求
- 禁止使用 emoji 作为功能图标
- 禁止默认系统字体直出
- 禁止“AI 模板感”页面：同质化色块、空洞 hero、无层级卡片堆砌
- 页面必须体现真正的商业产品结构，而不是演示图
- 优先实现真实截图区、案例区、信任区、状态反馈区，而不是只做装饰性 hero

可以借鉴的执行方式：

- 先输出 master 级设计规则，再输出页面级 override
- 先定页面结构和任务路径，再补视觉细节
- 对首页/落地页强调价值表达、案例证明、CTA
- 对后台/工作台强调效率、状态反馈、筛选、批量操作、审计感

---

## 执行规则

### 前端先行原则
- 三份核心文档完成后先过用户确认门，再进入 Spec 与实现阶段
- 先完成前端骨架并可演示，再实现后端 API
- 前端使用 Mock/占位数据，完成视觉验证后再联调
- 前端完成后必须主动运行并验证，再继续后端与联调
- UI 严格遵循 `output/*-uiux.md` 的设计规范
- 如果是网页类需求，默认目标是现代商业产品，而不是 AI 味很重的演示页

### 代码质量规则
- 禁止使用 emoji 作为图标（用 Lucide/Heroicons/Tabler 等图标库）
- 禁止将紫色/粉色渐变作为默认主视觉（除非 PRD 与品牌规范明确要求）
- 禁止直接输出“AI 模板感”页面（同质化区块、默认系统字体直出、无层级信息架构）
- 所有用户输入必须验证（防 SQL 注入、XSS）
- 使用参数化查询，禁止字符串拼接 SQL
- 测试覆盖率目标 ≥ 80%
- 遵循 Conventional Commits 提交规范

### 质量门禁规则
- **统一标准**：质量分 **≥ 80 分** 才可通过
- 必检项（文档/安全/性能/测试）出现失败即阻断
- 交付前运行：`super-dev quality --type all`
- 红队发现 Critical 问题必须修复后才能继续

### 任务跟踪规则
- 每完成一个任务，在 `.super-dev/changes/*/tasks.md` 标记 `[x]`
- 遇到不清楚的地方，优先查阅架构文档，再看 PRD
- 不要自行扩展需求范围，严格按 Spec 实现

---

## 常用命令参考

```bash
# 需求直达模式（推荐）
super-dev "实现一个包含登录、订单、支付的系统"

# 查看当前 Spec
super-dev spec view

# 运行质量检查
super-dev quality --type all

# 生成 CI/CD 配置
super-dev deploy --cicd github

# 调用专家
super-dev expert SECURITY "审查登录模块"
super-dev expert ARCHITECT "评审微服务拆分方案"
```

---

## 交付标准

所有任务完成后，确认：

- [ ] 所有 `.super-dev/changes/*/tasks.md` 中的任务标记为 `[x]`
- [ ] 前端可正常演示，无控制台报错
- [ ] 后端 API 联调通过
- [ ] 数据库迁移脚本可正常执行
- [ ] `output/delivery/*` 交付包状态为 ready
- [ ] CI/CD 流水线配置完整
- [ ] 质量门禁通过（`super-dev quality --type all`）
- [ ] 红队发现的 Critical/High 问题均已修复
"""
        (target_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
