# Super Dev 安装方式（2.0.10）

宿主详细试用方式请看：

- [HOST_USAGE_GUIDE.md](/Users/weiyou/Documents/kaifa/super-dev/docs/HOST_USAGE_GUIDE.md)

## 方式 1：uv 安装（推荐）

```bash
uv tool install super-dev
```

适用：本机命令行工具安装、独立环境、升级简单。

升级：

```bash
uv tool upgrade super-dev
```

## 方式 2：PyPI 安装

```bash
pip install -U super-dev
```

适用：标准企业环境、依赖管理平台统一从 PyPI 拉取。

安装完成后，直接执行：

```bash
super-dev
```

默认会进入交互式宿主安装引导：

1. 顶部显示 `Super Dev` 安装入口
2. `↑ / ↓` 选择宿主
3. `Space` 勾选宿主
4. `Enter` 开始安装
5. `A` 全选
6. `C` 仅选择 CLI 宿主
7. `I` 仅选择 IDE 宿主
8. `R` 清空选择

安装完成后，终端会直接输出该宿主的最终触发方式：

1. slash 宿主：`/super-dev 你的需求`
2. 非 slash 宿主：`super-dev: 你的需求`

## 方式 3：安装指定版本（复现/回滚）

```bash
pip install super-dev==2.0.10
```

适用：需要稳定复现、灰度回滚。

## 方式 4：GitHub 直装（Tag）

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.10
```

适用：希望直接基于 GitHub Tag 安装。

## 方式 5：源码开发安装

`uv`：

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
uv sync
uv run super-dev --help
```

`pip`：

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

适用：二次开发、调试、提交代码。

## 验证

```bash
super-dev --help
super-dev
```

如果已接入宿主，推荐在宿主内验证：

1. 支持原生映射的 CLI 宿主：`/super-dev 你的需求`
2. 非 slash CLI 宿主（如 Codex CLI、Kimi CLI）：在会话内输入 `super-dev: 你的需求`
3. IDE 宿主：在 Agent Chat 中执行 `/super-dev 你的需求`
4. 非 slash 宿主：输入 `super-dev: 你的需求`
5. 如果宿主是 Trae，接入会写入项目规则 `.trae/project_rules.md`、`.trae/rules.md`，以及用户规则 `~/.trae/user_rules.md`、`~/.trae/rules.md`，并在检测到兼容技能目录时增强安装 `~/.trae/skills/super-dev-core/SKILL.md`

默认流程不是直接编码，而是：

1. 先研究同类产品，输出 `output/*-research.md`
2. 再生成 PRD、架构、UI/UX 三份核心文档
3. 等用户确认三份核心文档
4. 再生成 Spec 与 `tasks.md`
5. 最后才进入编码、质量门禁与交付

宿主接入完成后，建议再执行一次标准验收：

```bash
super-dev integrate smoke --target <host_id>
```

它会输出该宿主的验收语句、验收步骤和通过标准。

## 升级到 2.0.10

```bash
# uv 方式
uv tool upgrade super-dev

# GitHub 方式
pip install --upgrade "git+https://github.com/shangyankeji/super-dev.git@v2.0.10"

# PyPI 方式
pip install --upgrade "super-dev==2.0.10"
```
