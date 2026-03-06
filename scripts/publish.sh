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
SKIP_PREFLIGHT=0
ALLOW_DIRTY=0
SKIP_BENCHMARK=0
YES=0
USE_UV=0

usage() {
    cat <<'EOF'
Usage: ./scripts/publish.sh [options]

Options:
  --repository <pypi|testpypi>  Upload target (default: pypi)
  --uv                          Force uv build/publish flow
  --skip-preflight              Skip preflight checks
  --allow-dirty                 Allow dirty git worktree in preflight
  --skip-benchmark              Skip benchmark in preflight
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
        --skip-preflight)
            SKIP_PREFLIGHT=1
            shift
            ;;
        --uv)
            USE_UV=1
            shift
            ;;
        --allow-dirty)
            ALLOW_DIRTY=1
            shift
            ;;
        --skip-benchmark)
            SKIP_BENCHMARK=1
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

if [[ "$REPOSITORY" == "pypi" ]]; then
    TOKEN="${PYPI_API_TOKEN:-}"
    REPO_URL_ARG=""
    PROJECT_URL="https://pypi.org/project/super-dev/"
else
    TOKEN="${TEST_PYPI_API_TOKEN:-${PYPI_API_TOKEN:-}}"
    REPO_URL_ARG="--repository-url https://test.pypi.org/legacy/"
    PROJECT_URL="https://test.pypi.org/project/super-dev/"
fi

if [[ -z "$TOKEN" ]]; then
    if [[ "$REPOSITORY" == "pypi" ]]; then
        echo "[ERROR] PYPI_API_TOKEN is not set"
    else
        echo "[ERROR] TEST_PYPI_API_TOKEN (or PYPI_API_TOKEN) is not set"
    fi
    exit 1
fi

if [[ "$USE_UV" -ne 1 ]] && command -v uv >/dev/null 2>&1 && [[ -f "$ROOT_DIR/uv.lock" ]]; then
    USE_UV=1
fi

VERSION="$("$PYTHON_BIN" -c "from super_dev import __version__; print(__version__)")"
echo "[INFO] Preparing release for super-dev ${VERSION} -> ${REPOSITORY}"
if [[ "$USE_UV" -eq 1 ]]; then
    echo "[INFO] Publish backend: uv"
else
    echo "[INFO] Publish backend: python build + twine"
fi

if [[ "$YES" -ne 1 ]]; then
    read -r -p "Proceed with publishing ${VERSION} to ${REPOSITORY}? (y/N): " confirm
    if [[ "${confirm,,}" != "y" ]]; then
        echo "[INFO] Publish cancelled"
        exit 0
    fi
fi

if [[ "$SKIP_PREFLIGHT" -ne 1 ]]; then
    PREFLIGHT_ARGS=("./scripts/preflight.sh" "--skip-package")
    if [[ "$USE_UV" -eq 1 ]]; then
        PREFLIGHT_ARGS+=("--uv")
    fi
    if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
        PREFLIGHT_ARGS+=("--allow-dirty")
    fi
    if [[ "$SKIP_BENCHMARK" -eq 1 ]]; then
        PREFLIGHT_ARGS+=("--skip-benchmark")
    fi
    echo "[INFO] Running preflight: ${PREFLIGHT_ARGS[*]}"
    "${PREFLIGHT_ARGS[@]}"
else
    echo "[WARN] Preflight skipped by --skip-preflight"
fi

echo "[INFO] Building package"
if [[ "$USE_UV" -eq 1 ]]; then
    uv build
    echo "[INFO] Running twine check via uvx"
    uvx twine check dist/*
    echo "[INFO] Uploading with uv publish"
    if [[ "$REPOSITORY" == "pypi" ]]; then
        UV_PUBLISH_TOKEN="$TOKEN" uv publish
    else
        UV_PUBLISH_TOKEN="$TOKEN" UV_PUBLISH_URL="https://test.pypi.org/legacy/" uv publish
    fi
else
    rm -rf dist/ build/ *.egg-info
    "$PYTHON_BIN" -m build

    echo "[INFO] Running twine check"
    twine check dist/*

    echo "[INFO] Uploading to ${REPOSITORY}"
    if [[ -n "$REPO_URL_ARG" ]]; then
        # shellcheck disable=SC2086
        twine upload --non-interactive --username __token__ --password "$TOKEN" $REPO_URL_ARG dist/*
    else
        twine upload --non-interactive --username __token__ --password "$TOKEN" dist/*
    fi
fi

echo "[PASS] Publish completed"
echo "[INFO] Package page: ${PROJECT_URL}"
