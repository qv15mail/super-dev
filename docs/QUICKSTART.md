# Super Dev 快速开始

> 面向 `2.3.8` 版本，5 分钟完成从安装到首次流水线运行。

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
pip install super-dev==2.3.8
```

## 3. 公开主路径

普通用户只需要记住两条终端命令：

```bash
super-dev
super-dev update
```

最短路径：

1. 在项目目录运行 `super-dev`
2. 在安装器里选择目标宿主，让系统自动写入项目级 / 全局级协议面
3. 打开宿主，在宿主里输入 `/super-dev 你的需求` 或 `super-dev: 你的需求`

宿主里的推荐表达：

```text
/super-dev 构建一个电商后台，包含登录、订单、支付
/super-dev 继续当前流程
/super-dev 现在下一步是什么

super-dev: 构建一个电商后台，包含登录、订单、支付
super-dev: 继续当前流程
super-dev: 文档确认，可以继续
```

成功标志：

- 第一轮回复明确说当前阶段是 `research`
- 三份核心文档完成后会停下来等你确认
- 没有跳过 `research -> 三文档 -> 确认门 -> Spec -> frontend -> backend -> quality`

如果你是第二天回来、重开电脑、重开宿主、或者刚完成返工，不要先回终端找流程命令，优先回到宿主里说：

- `继续当前流程`
- `现在下一步是什么`
- `文档确认，可以继续`
- `前端预览确认，可以继续`

只有安装、升级、诊断或内部维护时，才需要再回终端。

## 4. 内部 / 维护命令

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
super-dev design list                 # 列出设计灵感锚点（PR #11，2.3.8 新增）
super-dev design recommend            # 按当前项目推荐设计方向
super-dev design apply linear.app     # 应用并重生成 uiux/ui-contract
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
