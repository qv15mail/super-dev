# Super Dev 快速开始

> 面向 `2.1.1` 版本，5-10 分钟完成从安装到首次流水线运行。

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
pip install super-dev==2.1.1
```

## 3. 启动方式（推荐）

优先在宿主会话内使用：

```text
/super-dev 构建一个电商后台，包含登录、订单、支付
```

如果你不确定当前机器该用哪个宿主，先运行：

```bash
super-dev start --idea "构建一个电商后台，包含登录、订单、支付"
```

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
```

## 5. 流程控制

如果你已经跑到后面阶段，但想回到某一环节继续修改，不需要重开整条流水线。

```bash
# 看当前在哪一步、下一步是什么
super-dev status

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

## 7. 下一步

- 发布流程：[`docs/PUBLISHING.md`](./PUBLISHING.md)
- 发布作战手册：[`docs/RELEASE_RUNBOOK.md`](./RELEASE_RUNBOOK.md)
- 全量说明：[`README.md`](../README.md)
