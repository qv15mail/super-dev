# Super Dev 安装方式（2.0.1）

## 方式 1：PyPI 安装（推荐）

```bash
pip install -U super-dev
```

适用：标准企业环境、依赖管理平台统一从 PyPI 拉取。

## 方式 2：安装指定版本（复现/回滚）

```bash
pip install super-dev==2.0.1
```

适用：需要稳定复现、灰度回滚。

## 方式 3：GitHub 直装（Tag）

```bash
pip install git+https://github.com/shangyankeji/super-dev.git@v2.0.1
```

适用：希望直接基于 GitHub Tag 安装。

## 方式 4：源码开发安装

```bash
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev
pip install -e ".[dev]"
```

适用：二次开发、调试、提交代码。

## 验证

```bash
super-dev --help
super-dev "构建一个带登录和订单管理的系统"
```

## 升级到 2.0.1

```bash
# GitHub 方式
pip install --upgrade "git+https://github.com/shangyankeji/super-dev.git@v2.0.1"

# PyPI 方式
pip install --upgrade "super-dev==2.0.1"
```
