#!/bin/bash
# Super Dev 发布脚本
# 使用方法：./scripts/publish.sh

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "❌ python3/python not found in PATH"
    exit 1
fi

echo "🚀 Super Dev 发布脚本"
echo "======================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查版本号
echo -e "${YELLOW}📝 当前版本号：${NC}"
grep "version =" pyproject.toml | head -1
echo ""

read -p "版本号正确吗？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 发布已取消${NC}"
    echo "请编辑 pyproject.toml 更新版本号"
    exit 1
fi

# 2. 检查是否有未提交的更改
echo -e "${YELLOW}🔍 检查 Git 状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 有未提交的更改${NC}"
    echo "请先提交所有更改："
    echo "  git add ."
    echo "  git commit -m 'bump: version x.x.x'"
    exit 1
fi

# 3. 运行测试
echo -e "${YELLOW}🧪 运行测试...${NC}"
if command -v pytest &> /dev/null; then
    pytest
    echo -e "${GREEN}✅ 测试通过${NC}"
else
    echo -e "${YELLOW}⚠️  pytest 未安装，跳过测试${NC}"
fi

# 4. 检查代码质量
echo -e "${YELLOW}🔍 检查代码质量...${NC}"
if command -v ruff &> /dev/null; then
    ruff check .
    echo -e "${GREEN}✅ Ruff 检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  ruff 未安装，跳过代码检查${NC}"
fi

# 5. 清理旧的构建
echo -e "${YELLOW}🧹 清理旧的构建...${NC}"
rm -rf dist/ build/ *.egg-info
echo -e "${GREEN}✅ 清理完成${NC}"

# 5.5 交付门禁 smoke
echo -e "${YELLOW}🔐 验证交付门禁（smoke）...${NC}"
"$PYTHON_BIN" scripts/check_delivery_ready.py --smoke --project-dir "$ROOT_DIR"
echo -e "${GREEN}✅ 交付门禁通过${NC}"

# 6. 构建包
echo -e "${YELLOW}📦 构建包...${NC}"
if command -v uv &> /dev/null; then
    uv build
else
    "$PYTHON_BIN" -m build
fi
echo -e "${GREEN}✅ 构建完成${NC}"

# 7. 检查包
echo -e "${YELLOW}🔍 检查包...${NC}"
if command -v twine &> /dev/null; then
    twine check dist/*
    echo -e "${GREEN}✅ 包检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  twine 未安装，跳过包检查${NC}"
    echo "安装 twine: pip install twine"
fi

# 8. 显示将要发布的内容
echo ""
echo -e "${YELLOW}📦 将要发布的内容：${NC}"
ls -lh dist/

# 9. 确认发布
echo ""
read -p "确定要发布到 PyPI 吗？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ 发布已取消${NC}"
    exit 1
fi

# 10. 发布到 PyPI
echo -e "${YELLOW}🚀 发布到 PyPI...${NC}"
if command -v twine &> /dev/null; then
    twine upload dist/*
    echo -e "${GREEN}✅ 发布成功！${NC}"
else
    echo -e "${RED}❌ twine 未安装${NC}"
    echo "请先安装: pip install twine"
    exit 1
fi

# 11. 创建 Git tag
echo ""
echo -e "${YELLOW}🏷️  创建 Git tag...${NC}"
VERSION=$(grep "version =" pyproject.toml | sed 's/.*version = "\(.*\)".*/\1/')
read -p "要创建 Git tag v$VERSION 吗？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag "v$VERSION"
    git push origin "v$VERSION"
    echo -e "${GREEN}✅ Git tag 已创建并推送${NC}"
else
    echo -e "${YELLOW}⚠️  跳过 Git tag 创建${NC}"
fi

# 完成
echo ""
echo -e "${GREEN}🎉 发布完成！${NC}"
echo ""
echo "📦 PyPI: https://pypi.org/project/super-dev/"
echo "📖 文档: https://github.com/shangyankeji/super-dev"
echo ""
echo "🧪 测试安装："
echo "  pip install super-dev"
echo "  super-dev --version"
echo ""
