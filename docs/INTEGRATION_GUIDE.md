# Super Dev 集成指南（2.0.5）

> 宿主详细试用方式、是否支持 `/super-dev`、各宿主的正确入口，请优先查看：
> [HOST_USAGE_GUIDE.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_USAGE_GUIDE.md)

## 目标

把 `Super Dev` 安装到常见 AI Coding 工具中，让用户在宿主里使用统一入口：

```text
/super-dev 你的功能需求
```

如果用户不清楚该选哪个宿主，可先运行：

```bash
super-dev start --idea "你的功能需求"
```

注意：默认启用宿主硬门禁。若没有 `ready` 宿主，流水线会阻断并提示先完成接入。

该入口会自动执行完整流水线：

需求增强（联网 + 知识库） -> PRD/架构/UIUX -> Spec -> 前端优先 -> 后端与迁移 -> 红队审查 -> 质量门禁（80+） -> CI/CD（5 平台） -> 交付包

---

## 支持矩阵

支持矩阵以 CLI 实时输出为准：

```bash
super-dev integrate matrix
super-dev integrate matrix --json
```

---

## 快速安装

### 方式 A：一键安装（推荐）

```bash
./install.sh --targets all
```

默认动作：

- 为所有平台写入集成规则文件
- 安装内置 `super-dev` Skill

### 方式 B：只生成规则，不安装 Skill

```bash
./install.sh --targets all --no-skill
```

### 方式 C：使用 CLI 逐项安装

```bash
# 生成全部平台规则
super-dev integrate setup --all --force

# 给每个平台安装内置 Skill
super-dev skill install super-dev --target claude-code --name super-dev-core --force
super-dev skill install super-dev --target codex-cli --name super-dev-core --force
super-dev skill install super-dev --target gemini-cli --name super-dev-core --force
super-dev skill install super-dev --target kimi-cli --name super-dev-core --force
super-dev skill install super-dev --target kiro-cli --name super-dev-core --force
super-dev skill install super-dev --target qoder-cli --name super-dev-core --force
super-dev skill install super-dev --target qoder --name super-dev-core --force
```

---

## 规则文件落点

| 平台 | 集成规则文件 |
|:---|:---|
| claude-code | `.claude/CLAUDE.md` |
| codex-cli | `.codex/AGENTS.md` |
| gemini-cli | `.gemini/AGENTS.md` |
| kimi-cli | `.kimi/AGENTS.md` |
| kiro-cli | `.kiro/AGENTS.md` |
| qoder-cli | `.qoder/AGENTS.md` |
| qoder | `.qoder/rules.md` |

Skill 安装目录（按 target）由 `super-dev skill` 自动处理。

---

## 统一使用方式（新标准）

### 1. 终端编排入口

```bash
super-dev "做一个企业级任务管理系统，包含登录、RBAC、项目、任务、报表"
```

### 2. 需要精细参数时再用高级模式

```bash
super-dev pipeline "做一个企业级任务管理系统，包含登录、RBAC、项目、任务、报表" \
  --platform web \
  --frontend react \
  --backend python \
  --domain saas \
  --cicd all
```

### 3. 查看 Spec 任务执行状态

```bash
super-dev task list
super-dev task status <change_id>
super-dev task run <change_id>
```

---

## 商业级交付检查

执行完需求后，至少确认：

- `output/*-prd.md`、`output/*-architecture.md`、`output/*-uiux.md`
- `.super-dev/changes/*/tasks.md` 已生成并持续更新
- `output/*-redteam.md` 通过（无阻断）
- `output/*-quality-gate.md` 总分 >= 80
- 五大 CI/CD 文件已生成（github/gitlab/jenkins/azure/bitbucket）
- `output/delivery/*-delivery-manifest.json` 状态为 `ready`

---

## 常见问题

### 1. 我只想用“super-dev 需求”模式

可以，`2.0.2` 默认就是该模式。只要第一个参数不是子命令，就会自动进入完整流水线。

### 2. 我要给特定平台补装 Skill

```bash
super-dev skill targets
super-dev skill install super-dev --target <target> --name super-dev-core --force
super-dev skill list --target <target>
```

### 3. 我只想更新规则文件

```bash
super-dev integrate setup --target <target> --force
```

---

## 最佳实践

- 团队统一使用 `super-dev "需求"` 作为入口，减少命令分叉
- 将 `output/` 和 `.super-dev/changes/` 纳入代码评审上下文
- 在合并前强制检查红队报告和质量门禁报告
- 交付前使用 `output/delivery/` 作为对外版本快照
