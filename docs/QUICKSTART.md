# Super Dev 快速开始

> 面向 `2.0.8` 版本，5-10 分钟完成从安装到首次流水线运行。

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
pip install super-dev==2.0.8
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
super-dev spec init
super-dev spec list
super-dev quality --type all
super-dev deploy --cicd github
super-dev studio --port 8765
```

## 5. 发布前质量门禁

```bash
./scripts/preflight.sh
```

预检会执行：`ruff`、`mypy`、`pytest`、`delivery-smoke`、`bandit(-ll)`、`pip-audit`、benchmark、build、twine check。

## 6. 下一步

- 发布流程：[`docs/PUBLISHING.md`](./PUBLISHING.md)
- 发布作战手册：[`docs/RELEASE_RUNBOOK.md`](./RELEASE_RUNBOOK.md)
- 全量说明：[`README.md`](../README.md)
