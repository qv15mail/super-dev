# Super Dev 安装方式（2.0.0）

## 方式 1：GitHub 直装（推荐）

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.0
super-dev --version
```

适用：希望立即使用最新稳定版本，无需等待本地构建。

## 方式 2：PyPI 安装

```bash
pip install super-dev==2.0.0
super-dev --version
```

适用：标准企业环境、依赖管理平台统一从 PyPI 拉取。

## 方式 3：源码开发安装

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
super-dev --version
```

适用：二次开发、调试、提交代码。

## 验证

```bash
super-dev --help
super-dev pipeline --help
```

## 升级到 2.0.0

```bash
# GitHub 方式
pip install --upgrade "git+https://github.com/shangyankeji/super-dev.git@v2.0.0"

# PyPI 方式
pip install --upgrade "super-dev==2.0.0"
```
