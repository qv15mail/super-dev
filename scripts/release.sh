#!/usr/bin/env bash
# -*- coding: utf-8 -*-
"""
Super Dev 自动发布脚本
用于自动化发布流程：测试、构建、上传到 PyPI
"""

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[ERROR] python3/python not found in PATH"
    exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取版本号
get_version() {
    "$PYTHON_BIN" -c "from super_dev import __version__; print(__version__)"
}

# 检查是否在正确的分支上
check_branch() {
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" != "main" ]; then
        log_warning "当前不在 main 分支，当前分支: $BRANCH"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "发布已取消"
            exit 1
        fi
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."

    # 单元测试
    log_info "运行单元测试..."
    pytest tests/unit/ -v
    if [ $? -ne 0 ]; then
        log_error "单元测试失败"
        exit 1
    fi

    # 集成测试
    log_info "运行集成测试..."
    pytest tests/integration/ -v
    if [ $? -ne 0 ]; then
        log_error "集成测试失败"
        exit 1
    fi

    # 代码风格检查
    log_info "检查代码风格..."
    ruff check super_dev/
    if [ $? -ne 0 ]; then
        log_error "代码风格检查失败"
        exit 1
    fi

    # 类型检查
    log_info "运行类型检查..."
    mypy super_dev/
    if [ $? -ne 0 ]; then
        log_warning "类型检查有警告，继续..."
    fi

    log_success "所有测试通过!"
}

# 交付门禁烟雾验证
run_delivery_gate() {
    log_info "运行交付门禁 smoke..."
    "$PYTHON_BIN" scripts/check_delivery_ready.py --smoke --project-dir "$(pwd)"
    if [ $? -ne 0 ]; then
        log_error "交付门禁 smoke 失败"
        exit 1
    fi
    log_success "交付门禁 smoke 通过!"
}

# 构建包
build_package() {
    log_info "构建包..."

    # 清理旧的构建文件
    rm -rf dist/ build/ *.egg-info

    # 构建
    "$PYTHON_BIN" -m build

    if [ $? -ne 0 ]; then
        log_error "构建失败"
        exit 1
    fi

    log_success "包构建完成!"
}

# 检查包
check_package() {
    log_info "检查包..."

    twine check dist/*

    if [ $? -ne 0 ]; then
        log_error "包检查失败"
        exit 1
    fi

    log_success "包检查通过!"
}

# 上传到 TestPyPI
upload_test_pypi() {
    log_info "上传到 TestPyPI..."

    read -p "TestPyPI 用户名: " TEST_USERNAME
    read -p "TestPyPI 密码: " -s TEST_PASSWORD
    echo

    twine upload --repository testpypi dist/* \
        --username "$TEST_USERNAME" \
        --password "$TEST_PASSWORD"

    if [ $? -eq 0 ]; then
        log_success "已上传到 TestPyPI!"
        log_info "测试安装: pip install --index-url https://test.pypi.org/simple/ super-dev"
    fi
}

# 上传到 PyPI
upload_pypi() {
    log_info "上传到 PyPI..."

    read -p "PyPI 用户名: " PYPI_USERNAME
    read -p "PyPI 密码: " -s PYPI_PASSWORD
    echo

    twine upload dist/* \
        --username "$PYPI_USERNAME" \
        --password "$PYPI_PASSWORD"

    if [ $? -eq 0 ]; then
        log_success "已上传到 PyPI!"
        log_info "安装: pip install super-dev"
    fi
}

# 创建 Git Tag
create_tag() {
    VERSION=$(get_version)
    TAG="v$VERSION"

    log_info "创建 Git Tag: $TAG"

    # 检查 tag 是否已存在
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        log_warning "Tag $TAG 已存在"
        read -p "是否删除并重新创建? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -d "$TAG"
            git push origin ":refs/tags/$TAG" || true
        else
            return
        fi
    fi

    # 创建 tag
    git tag -a "$TAG" -m "Release $VERSION"

    # 推送 tag
    git push origin "$TAG"

    log_success "Tag $TAG 已创建并推送!"
}

# 更新 CHANGELOG
update_changelog() {
    VERSION=$(get_version)
    DATE=$(date +%Y-%m-%d)

    log_info "更新 CHANGELOG.md..."

    # 在 CHANGELOG.md 中添加新版本
    sed -i.bak "s/\[Unreleased\]/[$VERSION] - $DATE/" CHANGELOG.md
    sed -i.bak "s/\[Unreleased\]/[Unreleased]\n\n## [$VERSION] - $DATE/" CHANGELOG.md
    rm -f CHANGELOG.md.bak

    git add CHANGELOG.md
    git commit -m "chore: update CHANGELOG for $VERSION"

    log_success "CHANGELOG 已更新!"
}

# 主流程
main() {
    log_info "======================================"
    log_info "Super Dev 自动发布脚本"
    log_info "======================================"
    echo ""

    # 显示当前版本
    VERSION=$(get_version)
    log_info "当前版本: $VERSION"
    echo ""

    # 确认发布
    read -p "确认发布版本 $VERSION? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "发布已取消"
        exit 1
    fi

    # 检查分支
    check_branch

    # 运行测试
    run_tests

    # 交付门禁验证
    run_delivery_gate

    # 更新 CHANGELOG
    update_changelog

    # 构建包
    build_package

    # 检查包
    check_package

    # 创建 Git Tag
    create_tag

    # 选择上传目标
    echo ""
    log_info "选择上传目标:"
    echo "1) TestPyPI (测试)"
    echo "2) PyPI (正式)"
    echo "3) 跳过上传"
    echo ""
    read -p "请选择 (1-3): " CHOICE

    case $CHOICE in
        1)
            upload_test_pypi
            ;;
        2)
            upload_pypi
            ;;
        3)
            log_info "跳过上传"
            ;;
        *)
            log_error "无效选择"
            exit 1
            ;;
    esac

    echo ""
    log_success "======================================"
    log_success "发布完成!"
    log_success "======================================"
    echo ""
    log_info "后续步骤:"
    log_info "1. 在 GitHub 创建 Release: https://github.com/shangyankeji/super-dev/releases/new"
    log_info "2. 发布公告到社交媒体"
    log_info "3. 更新文档和示例"
}

# 运行主流程
main
