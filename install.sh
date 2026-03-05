#!/usr/bin/env bash
#
# Super Dev 宿主安装向导
#
# 用法:
#   ./install.sh                                # 交互式向导（支持多选宿主）
#   ./install.sh --targets claude-code,codex-cli,cursor-cli,opencode,iflow,qoder,windsurf,codebuddy
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

ALL_TARGETS_CSV="claude-code,codebuddy-cli,codebuddy,codex-cli,cursor-cli,windsurf,gemini-cli,iflow,kimi-cli,kiro-cli,opencode,qoder-cli,cursor,kiro,qoder,trae"
CLI_TARGETS_CSV="claude-code,codebuddy-cli,codex-cli,cursor-cli,gemini-cli,iflow,kimi-cli,kiro-cli,opencode,qoder-cli"
IDE_TARGETS_CSV="codebuddy,cursor,kiro,qoder,trae,windsurf"

TARGETS="$ALL_TARGETS_CSV"
WITH_SKILL="true"
GUIDED="auto"
TARGETS_EXPLICIT="false"

IFS=',' read -r -a ALL_TARGET_ARRAY <<< "$ALL_TARGETS_CSV"
IFS=',' read -r -a CLI_TARGET_ARRAY <<< "$CLI_TARGETS_CSV"
IFS=',' read -r -a IDE_TARGET_ARRAY <<< "$IDE_TARGETS_CSV"

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

is_valid_target() {
  local target="$1"
  local item
  for item in "${ALL_TARGET_ARRAY[@]}"; do
    if [[ "$item" == "$target" ]]; then
      return 0
    fi
  done
  return 1
}

append_unique_target() {
  local target="$1"
  local existing
  for existing in "${SELECTED_TARGETS[@]-}"; do
    if [[ "$existing" == "$target" ]]; then
      return 0
    fi
  done
  SELECTED_TARGETS+=("$target")
}

join_targets_csv() {
  local arr=("$@")
  local out=""
  local item
  for item in "${arr[@]}"; do
    if [[ -z "$out" ]]; then
      out="$item"
    else
      out="${out},${item}"
    fi
  done
  printf '%s' "$out"
}

parse_targets_csv() {
  local raw="$1"
  local normalized
  local token

  normalized="$(echo "$raw" | tr 'A-Z' 'a-z' | tr ' ' ',')"
  IFS=',' read -r -a raw_tokens <<< "$normalized"

  SELECTED_TARGETS=()
  for token in "${raw_tokens[@]}"; do
    token="$(trim "$token")"
    if [[ -z "$token" ]]; then
      continue
    fi
    if [[ "$token" == "all" ]]; then
      SELECTED_TARGETS=("${ALL_TARGET_ARRAY[@]}")
      TARGETS="$(join_targets_csv "${SELECTED_TARGETS[@]}")"
      return 0
    fi
    if [[ "$token" == "cli" ]]; then
      local cli_target
      for cli_target in "${CLI_TARGET_ARRAY[@]}"; do
        append_unique_target "$cli_target"
      done
      continue
    fi
    if [[ "$token" == "ide" ]]; then
      local ide_target
      for ide_target in "${IDE_TARGET_ARRAY[@]}"; do
        append_unique_target "$ide_target"
      done
      continue
    fi
    if ! is_valid_target "$token"; then
      return 1
    fi
    append_unique_target "$token"
  done

  if [[ "${#SELECTED_TARGETS[@]}" -eq 0 ]]; then
    return 1
  fi

  TARGETS="$(join_targets_csv "${SELECTED_TARGETS[@]}")"
  return 0
}

prompt_yes_no() {
  local prompt="$1"
  local default_yes="$2"
  local answer=""
  local normalized=""

  if [[ "$default_yes" == "true" ]]; then
    read -r -p "$prompt [Y/n]: " answer
  else
    read -r -p "$prompt [y/N]: " answer
  fi
  normalized="$(echo "${answer:-}" | tr 'A-Z' 'a-z')"
  normalized="$(trim "$normalized")"

  if [[ -z "$normalized" ]]; then
    [[ "$default_yes" == "true" ]] && return 0 || return 1
  fi
  case "$normalized" in
    y|yes|1|true) return 0 ;;
    n|no|0|false) return 1 ;;
    *) [[ "$default_yes" == "true" ]] && return 0 || return 1 ;;
  esac
}

run_guided_selector() {
  local index=1
  local input=""
  local normalized=""
  local token=""
  local target=""

  echo ""
  echo -e "${GREEN}Super Dev 安装向导${NC}"
  echo "=================================="
  echo "请选择要接入的宿主工具（支持多选）"
  echo ""
  echo "CLI 宿主:"
  for target in "${CLI_TARGET_ARRAY[@]}"; do
    printf "  %2d. %s\n" "$index" "$target"
    index=$((index + 1))
  done
  echo ""
  echo "IDE 宿主:"
  for target in "${IDE_TARGET_ARRAY[@]}"; do
    printf "  %2d. %s\n" "$index" "$target"
    index=$((index + 1))
  done
  echo ""
  echo "快捷输入:"
  echo "  cli  = 全选 CLI"
  echo "  ide  = 全选 IDE"
  echo "  all  = 全选全部"
  echo "  也可直接输入宿主 id（如 codex-cli,cursor-cli,opencode,qoder,windsurf）"

  while true; do
    read -r -p "请输入编号/宿主ID（逗号分隔，可多选）: " input
    normalized="$(echo "$input" | tr 'A-Z' 'a-z' | tr ' ' ',')"
    IFS=',' read -r -a tokens <<< "$normalized"
    SELECTED_TARGETS=()

    for token in "${tokens[@]}"; do
      token="$(trim "$token")"
      if [[ -z "$token" ]]; then
        continue
      fi

      if [[ "$token" == "all" ]]; then
        SELECTED_TARGETS=("${ALL_TARGET_ARRAY[@]}")
        break
      elif [[ "$token" == "cli" ]]; then
        for target in "${CLI_TARGET_ARRAY[@]}"; do
          append_unique_target "$target"
        done
        continue
      elif [[ "$token" == "ide" ]]; then
        for target in "${IDE_TARGET_ARRAY[@]}"; do
          append_unique_target "$target"
        done
        continue
      fi

      if [[ "$token" =~ ^[0-9]+$ ]]; then
        if [[ "$token" -lt 1 || "$token" -gt "${#ALL_TARGET_ARRAY[@]}" ]]; then
          SELECTED_TARGETS=()
          break
        fi
        append_unique_target "${ALL_TARGET_ARRAY[$((token - 1))]}"
        continue
      fi

      if is_valid_target "$token"; then
        append_unique_target "$token"
      else
        SELECTED_TARGETS=()
        break
      fi
    done

    if [[ "${#SELECTED_TARGETS[@]}" -gt 0 ]]; then
      TARGETS="$(join_targets_csv "${SELECTED_TARGETS[@]}")"
      break
    fi
    warning "输入无效，请重新选择。"
  done

  if prompt_yes_no "是否安装内置 Skill（super-dev-core）?" "true"; then
    WITH_SKILL="true"
  else
    WITH_SKILL="false"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --targets)
      TARGETS="${2:-$ALL_TARGETS_CSV}"
      TARGETS_EXPLICIT="true"
      shift 2
      ;;
    --no-skill)
      WITH_SKILL="false"
      shift
      ;;
    --guided)
      GUIDED="true"
      shift
      ;;
    --no-guided)
      GUIDED="false"
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Super Dev Installer

Options:
  --targets <list>   目标平台，逗号分隔，或 all/cli/ide
                     可选: claude-code,codebuddy-cli,codebuddy,codex-cli,cursor-cli,windsurf,gemini-cli,iflow,kimi-cli,kiro-cli,opencode,qoder-cli,cursor,kiro,qoder,trae
  --no-skill         只生成宿主集成和 /super-dev 映射，不安装内置 skill
  --guided           强制进入交互式安装向导
  --no-guided        跳过交互向导（需配合 --targets）
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

if ! command -v super-dev >/dev/null 2>&1; then
  error "未检测到 super-dev 命令。请先安装 super-dev 后再运行本脚本。"
  error "示例: pip install -e ."
  exit 1
fi

if [[ "$GUIDED" == "true" ]]; then
  run_guided_selector
elif [[ "$GUIDED" == "auto" && "$TARGETS_EXPLICIT" == "false" ]]; then
  if [[ -t 0 ]]; then
    run_guided_selector
  else
    warning "检测到非交互终端，自动使用 all 目标。可通过 --targets 指定。"
    TARGETS="$ALL_TARGETS_CSV"
  fi
fi

if ! parse_targets_csv "$TARGETS"; then
  error "无效的 --targets: $TARGETS"
  exit 1
fi

echo ""
echo -e "${GREEN}Super Dev Installer${NC}"
echo "=================================="
echo "Targets: $TARGETS"
echo "Install skill: $WITH_SKILL"
echo ""

if [[ -t 0 ]]; then
  if ! prompt_yes_no "确认开始安装?" "true"; then
    warning "已取消安装。"
    exit 0
  fi
fi

IFS=',' read -r -a target_list <<< "$TARGETS"

for target in "${target_list[@]}"; do
  target="$(trim "$target")"
  if [[ -z "$target" ]]; then
    continue
  fi

  info "接入宿主: $target"
  onboard_cmd=(super-dev onboard --host "$target" --yes --force)
  doctor_cmd=(super-dev doctor --host "$target")

  if [[ "$WITH_SKILL" != "true" ]]; then
    onboard_cmd+=(--skip-skill)
    doctor_cmd+=(--skip-skill)
  fi

  if "${onboard_cmd[@]}" >/dev/null; then
    success "接入完成: $target"
  else
    warning "接入失败: $target"
    continue
  fi

  if "${doctor_cmd[@]}" >/dev/null; then
    success "诊断通过: $target"
  else
    warning "诊断未通过: $target（可手动执行: super-dev doctor --host $target）"
  fi
done

echo ""
echo -e "${GREEN}=================================="
echo " 安装完成"
echo "==================================${NC}"
echo ""
echo "下一步:"
echo "  1. super-dev detect --auto --save-profile"
echo "  2. super-dev policy init --preset enterprise --force"
echo "  3. 在宿主中执行 /super-dev <你的需求>（或终端 super-dev \"<你的需求>\"）"
