#!/usr/bin/env bash
#
# Super Dev 多平台安装脚本
#
# 用法:
#   ./install.sh
#   ./install.sh --targets claude-code,codex-cli,cursor
#   ./install.sh --targets all --no-skill
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}${NC} $1"; }
success() { echo -e "${GREEN}${NC} $1"; }
warning() { echo -e "${YELLOW}${NC} $1"; }
error() { echo -e "${RED}${NC} $1"; }

ALL_TARGETS="claude-code,codex-cli,opencode,cursor,qoder,trae,codebuddy,antigravity"
TARGETS="$ALL_TARGETS"
WITH_SKILL="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --targets)
      TARGETS="${2:-$ALL_TARGETS}"
      shift 2
      ;;
    --no-skill)
      WITH_SKILL="false"
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Super Dev Installer

Options:
  --targets <list>   目标平台，逗号分隔，或 all
                     可选: claude-code,codex-cli,opencode,cursor,qoder,trae,codebuddy,antigravity
  --no-skill         只生成集成配置，不安装内置 skill
  -h, --help         显示帮助
EOF
      exit 0
      ;;
    *)
      error "未知参数: $1"
      exit 1
      ;;
  esac
done

if [[ "$TARGETS" == "all" ]]; then
  TARGETS="$ALL_TARGETS"
fi

echo ""
echo -e "${GREEN}Super Dev Installer${NC}"
echo "=================================="
echo "Targets: $TARGETS"
echo "Install skill: $WITH_SKILL"
echo ""

if ! command -v super-dev >/dev/null 2>&1; then
  error "未检测到 super-dev 命令。请先安装 super-dev 后再运行本脚本。"
  error "示例: pip install -e ."
  exit 1
fi

IFS=',' read -r -a target_list <<< "$TARGETS"

for target in "${target_list[@]}"; do
  target="$(echo "$target" | xargs)"
  if [[ -z "$target" ]]; then
    continue
  fi

  info "配置集成: $target"
  if super-dev integrate setup --target "$target" --force >/dev/null; then
    success "集成配置完成: $target"
  else
    warning "集成配置失败: $target"
  fi

  if [[ "$WITH_SKILL" == "true" ]]; then
    info "安装内置 skill: $target"
    if super-dev skill install super-dev --target "$target" --name super-dev-core --force >/dev/null; then
      success "Skill 安装完成: $target"
    else
      warning "Skill 安装失败: $target"
    fi
  fi
done

echo ""
echo -e "${GREEN}=================================="
echo " 安装完成"
echo "==================================${NC}"
echo ""
echo "下一步:"
echo "  1) super-dev skill list --target codex-cli"
echo "  2) super-dev integrate list"
echo "  3) super-dev \"你的功能需求\""
