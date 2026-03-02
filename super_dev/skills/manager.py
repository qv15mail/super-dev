"""
Skill 安装管理器
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SkillInstallResult:
    name: str
    target: str
    path: Path
    source: str


class SkillManager:
    """跨平台 AI Coding 工具 Skill 管理"""

    TARGET_PATHS = {
        "claude-code": ".claude/skills",
        "codex-cli": ".codex/skills",
        "opencode": ".opencode/skills",
        "cursor": ".super-dev/skills/cursor",
        "qoder": ".super-dev/skills/qoder",
        "trae": ".super-dev/skills/trae",
        "codebuddy": ".super-dev/skills/codebuddy",
        "antigravity": ".super-dev/skills/antigravity",
    }

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()

    def list_targets(self) -> list[str]:
        return list(self.TARGET_PATHS.keys())

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
        skill_content = f"""# {skill_name} - Super Dev AI Coding Skill

> 版本: 2.0.1 | 适用工具: Claude Code, Codex CLI, OpenCode, Cursor, Antigravity 等所有 AI Coding 工具

---

## Skill 角色定义

你是一个由 **10 位顶级专家**组成的 AI 开发战队成员。当用户调用 Super Dev 时，你需要根据任务类型自动切换专家角色：

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
第 0 阶段  需求增强    → 解析需求 + 注入知识库 + 联网检索
第 1 阶段  文档生成    → PRD + 架构设计 + UI/UX 文档
第 2 阶段  前端骨架    → 先交付可演示前端（前端先行原则）
第 3 阶段  Spec 创建   → OpenSpec 风格规范 + 任务列表
第 4 阶段  实现骨架    → 前后端目录结构 + API 契约
第 5 阶段  红队审查    → 安全 + 性能 + 架构三维审查
第 6 阶段  质量门禁    → 统一阈值（80+）
第 7 阶段  代码审查    → 生成代码审查指南
第 8 阶段  AI 提示词   → 生成给 AI 开发的提示词
第 9 阶段  CI/CD       → 5 大平台配置（GitHub/GitLab/Jenkins/Azure/Bitbucket）
第 10 阶段 部署修复模板 → 环境变量示例 + 平台检查清单
第 11 阶段 交付收敛    → 6 种 ORM 迁移脚本 + 交付包（manifest/report/zip）
```

---

## 开始前必读（强制）

**在写任何一行代码之前**，必须先读取以下文档：

1. `output/*-prd.md` — 产品需求文档（功能边界、验收标准）
2. `output/*-architecture.md` — 架构设计文档（技术栈、API 规范）
3. `output/*-uiux.md` — UI/UX 设计文档（设计系统、组件规范）
4. `output/*-execution-plan.md` — 执行路线图（阶段任务和里程碑）
5. `.super-dev/changes/*/tasks.md` — Spec 任务列表（逐项实现）

---

## 执行规则

### 前端先行原则
- 先完成前端骨架并可演示，再实现后端 API
- 前端使用 Mock/占位数据，完成视觉验证后再联调
- UI 严格遵循 `output/*-uiux.md` 的设计规范

### 代码质量规则
- 禁止使用 emoji 作为图标（用 Lucide/Heroicons/Tabler 等图标库）
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
