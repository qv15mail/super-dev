# Super Dev 快速开始

> 面向 `2.0.0` 版本，5-10 分钟完成从安装到首次流水线运行。

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
super-dev --version
```

### 方式 B：安装指定版本（复现/回滚）

```bash
pip install super-dev==2.0.0
super-dev --version
```

预期输出示例：

```text
super-dev 2.0.0
```

## 3. 需求直达（推荐）

```bash
super-dev "构建一个电商后台，包含登录、订单、支付"
```

执行后会在 `output/`、`.super-dev/`、前后端骨架目录中生成完整产物，且在 `output/delivery/` 自动生成交付清单、交付报告和 zip 交付包。

如需精细控制平台参数，可使用显式 pipeline：

```bash
super-dev pipeline "构建一个电商后台，包含登录、订单、支付" --platform web --frontend react --backend python --domain ecommerce --cicd github
```

## 4. 常用命令

```bash
super-dev --help
super-dev create "用户认证系统"
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
