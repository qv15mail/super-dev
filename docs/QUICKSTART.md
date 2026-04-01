# Super Dev 快速开始

> 面向 `2.3.0` 版本，5 分钟完成从安装到首次流水线运行。

## 1. 环境要求

- Python `3.10+`
- 推荐：`pip install -e ".[dev]"`（开发场景）

```bash
python3 --version
```

## 2. 安装

### 方式 A：PyPI 安装（推荐）

```bash
pip install -U super-dev
```

### 方式 B：安装指定版本（复现/回滚）

```bash
pip install super-dev==2.3.0
```

## 3. 启动方式（推荐）

### 最短路径

如果你只想最快跑通一次，不想自己摸索，直接按这 3 步：

```bash
# 步骤 1: 初始化项目
super-dev init my-project

# 或使用项目模板快速初始化（可选模板: ecommerce/saas/dashboard/mobile/api/blog/miniapp）
super-dev init --template ecommerce

# 步骤 2: 自动检测并安装到所有宿主（会自动安装 enforcement hooks）
super-dev detect --auto

# 步骤 3: 在宿主中开始
# Claude Code / Codex 等支持 / 命令的宿主:
/super-dev 构建一个电商后台，包含登录、订单、支付

# 其他宿主:
super-dev: 构建一个电商后台，包含登录、订单、支付
```

然后：

1. 按 SKILL.md 的指引进入 pipeline 模式
2. 复制输出里的那句触发命令到宿主会话
3. 确认宿主第一轮回复明确说当前阶段是 `research`

成功标志：

- 会先做同类产品研究，而不是直接写代码
- 三份核心文档完成后会停下来等你确认
- 没有跳过 `research -> 三文档 -> 确认门 -> Spec -> frontend -> backend -> quality`

优先在宿主会话内使用：

```text
/super-dev 构建一个电商后台，包含登录、订单、支付
```

如果你不确定当前机器该用哪个宿主，先运行：

```bash
super-dev start --idea "构建一个电商后台，包含登录、订单、支付"
```

如果你已经在项目里，但不知道现在该先做哪一步，直接运行：

```bash
super-dev resume
```

如果你是下班回来、第二天继续、重开电脑或重开宿主后继续开发，优先用这一条。

```bash
super-dev next
```

它只输出当前最应该执行的一步，不需要你自己翻状态和门禁。

常见恢复场景：

| 场景 | 该用哪条命令 |
|------|--------------|
| 第二天回来继续开发 | `super-dev resume` |
| 宿主关掉了，重开后继续 | `super-dev resume` |
| 电脑重启了，回到项目继续 | `super-dev resume` |
| 不知道现在该先做什么 | `super-dev next` |
| 机器侧 pipeline 被中断 | `super-dev run --resume` |
| 当前在文档 / UI / 架构确认门里继续补充 | `super-dev resume`，然后直接继续说自然语言 |

恢复前优先看两份文件：

- `.super-dev/SESSION_BRIEF.md`
- `.super-dev/workflow-state.json`

这两份是当前流程的恢复真源。

如果你想先显式初始化项目契约，再进入宿主：

```bash
super-dev bootstrap --name my-project --platform web --frontend next --backend node
```

终端直达只负责本地治理产物编排，不替代宿主编码：

```bash
super-dev "构建一个电商后台，包含登录、订单、支付"
```

执行后会在 `output/`、`.super-dev/`、前后端骨架目录中生成完整产物，且在 `output/delivery/` 自动生成交付清单、交付报告和 zip 交付包。
同时会生成 `output/*-task-execution.md`，用于记录 Spec 任务执行、自动修复和未完成项。

如需精细控制平台参数，可使用显式 pipeline：

```bash
super-dev pipeline "构建一个电商后台，包含登录、订单、支付" --platform web --frontend react --backend python --domain ecommerce --cicd github
```

## 4. 常用命令

```bash
super-dev --help
super-dev start --idea "用户认证系统"
super-dev status
super-dev run research
super-dev run prd
super-dev run architecture
super-dev run uiux
super-dev run frontend
super-dev run backend
super-dev run quality
super-dev jump docs
super-dev jump frontend
super-dev confirm docs --comment "三文档已确认"
super-dev confirm preview --comment "前端预览已确认"
super-dev spec init
super-dev spec list
super-dev quality --type all
super-dev deploy --cicd github
super-dev studio --port 8765

# 2.3.0 新增命令
super-dev init --template ecommerce   # 使用项目模板
super-dev doctor --fix                # 自动修复安装问题
super-dev completion bash             # Shell 补全 (bash/zsh/fish)
super-dev feedback                    # 快速反馈到 GitHub Issues
super-dev migrate                     # 2.2.0 → 2.3.0 一键迁移
super-dev enforce install             # 安装宿主 hooks
super-dev enforce validate            # 运行约束验证
```

## 5. 流程控制

如果你已经跑到后面阶段，但想回到某一环节继续修改，不需要重开整条流水线。

```bash
# 看当前在哪一步、下一步是什么
super-dev status
super-dev next

# 只重跑研究或单个核心文档
super-dev run research
super-dev run prd
super-dev run architecture
super-dev run uiux

# 只重跑实现阶段
super-dev run frontend
super-dev run backend
super-dev run quality

# 直接回到某个阶段继续
super-dev jump docs
super-dev jump frontend

# 手动确认阶段通过，然后继续
super-dev confirm docs --comment "三文档已确认"
super-dev confirm preview --comment "前端预览已确认"
super-dev run --resume
```

## 6. 发布前质量门禁

```bash
./scripts/preflight.sh
```

预检会执行：`ruff`、`mypy`、`pytest`、`delivery-smoke`、`bandit(-ll)`、`pip-audit`、benchmark、build、twine check。

如果你在真实项目里用 Super Dev 编码，额外建议宿主在每轮实现后补做这 4 项：

1. 跑项目原生 `build / compile / type-check / test / runtime smoke`
2. 确认新增函数、方法、字段、模块都已经接入调用链
3. 确认没有新增 `unused code` 或新增 warning
4. 对本次 diff 做一次最小自审，再汇报完成

## 7. 下一步

- 发布流程：[`docs/PUBLISHING.md`](./PUBLISHING.md)
- 发布作战手册：[`docs/RELEASE_RUNBOOK.md`](./RELEASE_RUNBOOK.md)
- 全量说明：[`README.md`](../README.md)
