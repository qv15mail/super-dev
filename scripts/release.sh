#!/usr/bin/env bash

set -euo pipefail

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

REPOSITORY="pypi"
ALLOW_DIRTY=0
SKIP_PREFLIGHT=0
SKIP_BENCHMARK=0
PUSH_TAG=0
YES=0

usage() {
    cat <<'EOF'
Usage: ./scripts/release.sh [options]

Options:
  --repository <pypi|testpypi>  Upload target (default: pypi)
  --allow-dirty                 Allow dirty git worktree in preflight
  --skip-preflight              Skip preflight checks
  --skip-benchmark              Skip benchmark in preflight
  --push-tag                    Create and push git tag v<version>
  --yes                         Non-interactive mode (no confirmation prompt)
  -h, --help                    Show this help

Environment:
  PYPI_API_TOKEN                API token for PyPI upload
  TEST_PYPI_API_TOKEN           API token for TestPyPI upload (fallback: PYPI_API_TOKEN)
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repository)
            REPOSITORY="${2:-}"
            shift 2
            ;;
        --allow-dirty)
            ALLOW_DIRTY=1
            shift
            ;;
        --skip-preflight)
            SKIP_PREFLIGHT=1
            shift
            ;;
        --skip-benchmark)
            SKIP_BENCHMARK=1
            shift
            ;;
        --push-tag)
            PUSH_TAG=1
            shift
            ;;
        --yes)
            YES=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown argument: $1"
            usage
            exit 2
            ;;
    esac
done

if [[ "$REPOSITORY" != "pypi" && "$REPOSITORY" != "testpypi" ]]; then
    echo "[ERROR] --repository must be pypi or testpypi"
    exit 2
fi

VERSION="$("$PYTHON_BIN" -c "from super_dev import __version__; print(__version__)")"
TAG="v${VERSION}"
BRANCH="$(git branch --show-current 2>/dev/null || true)"

echo "[INFO] Release version: ${VERSION}"
echo "[INFO] Current branch: ${BRANCH:-unknown}"
echo "[INFO] Target repository: ${REPOSITORY}"

if [[ "$ALLOW_DIRTY" -ne 1 && -n "$(git status --porcelain)" ]]; then
    echo "[ERROR] Working tree is dirty. Commit or stash changes, or use --allow-dirty."
    exit 1
fi

if [[ "$YES" -ne 1 ]]; then
    read -r -p "Proceed with release ${VERSION}? (y/N): " confirm
    if [[ "${confirm,,}" != "y" ]]; then
        echo "[INFO] Release cancelled"
        exit 0
    fi
fi

PUBLISH_ARGS=("./scripts/publish.sh" "--repository" "$REPOSITORY")
if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
    PUBLISH_ARGS+=("--allow-dirty")
fi
if [[ "$SKIP_PREFLIGHT" -eq 1 ]]; then
    PUBLISH_ARGS+=("--skip-preflight")
fi
if [[ "$SKIP_BENCHMARK" -eq 1 ]]; then
    PUBLISH_ARGS+=("--skip-benchmark")
fi
if [[ "$YES" -eq 1 ]]; then
    PUBLISH_ARGS+=("--yes")
fi

echo "[INFO] Running publish step"
"${PUBLISH_ARGS[@]}"

if [[ "$PUSH_TAG" -eq 1 ]]; then
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "[ERROR] Git tag ${TAG} already exists"
        exit 1
    fi
    echo "[INFO] Creating git tag ${TAG}"
    git tag -a "$TAG" -m "Release ${VERSION}"
    git push origin "$TAG"
    echo "[PASS] Git tag pushed: ${TAG}"
else
    echo "[INFO] Tag step skipped (use --push-tag to enable)"
fi

echo "[PASS] Release flow completed for ${VERSION}"
