#!/usr/bin/env python3
"""
开发：Excellent（11964948@qq.com）
功能：Super Dev Web API - FastAPI 后端
作用：提供 REST API 服务，支持项目管理和工作流执行
创建时间：2025-12-30
最后修改：2025-12-30
"""

import asyncio
import glob
import json
import logging
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Literal, cast
from urllib.parse import urlencode

import uvicorn
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from super_dev import __description__, __version__
from super_dev.analyzer import (
    DependencyGraphBuilder,
    ImpactAnalyzer,
    RegressionGuardBuilder,
    RepoMapBuilder,
)
from super_dev.catalogs import (
    BACKEND_TEMPLATE_CATALOG,
    CICD_PLATFORM_CATALOG,
    CICD_PLATFORM_IDS,
    CICD_PLATFORM_TARGET_IDS,
    DOMAIN_CATALOG,
    HOST_COMMAND_CANDIDATES,
    HOST_TOOL_CATALOG,
    HOST_TOOL_CATEGORY_MAP,
    LANGUAGE_PREFERENCE_CATALOG,
    PIPELINE_FRONTEND_TEMPLATE_CATALOG,
    PLATFORM_CATALOG,
    PRIMARY_HOST_TOOL_IDS,
    host_detection_path_candidates,
    host_path_override_guide,
    host_runtime_validation_overrides,
)
from super_dev.config import ConfigManager
from super_dev.deployers import CICDGenerator
from super_dev.experts import (
    has_expert,
    list_expert_advice_history,
    read_expert_advice,
    save_expert_advice,
)
from super_dev.experts import (
    list_experts as list_expert_catalog,
)
from super_dev.framework_harness import FrameworkHarnessBuilder
from super_dev.harness_registry import (
    build_operational_harness_payload,
    derive_operational_focus,
    summarize_operational_harnesses,
)
from super_dev.hook_harness import HookHarnessBuilder
from super_dev.hooks.manager import HookManager
from super_dev.host_registry import HostInstallMode, get_display_name, get_install_mode
from super_dev.integrations.manager import IntegrationManager
from super_dev.operational_harness import OperationalHarnessBuilder
from super_dev.orchestrator import Phase, WorkflowContext, WorkflowEngine
from super_dev.policy import PipelinePolicy, PipelinePolicyManager
from super_dev.proof_pack import ProofPackBuilder
from super_dev.release_readiness import ReleaseReadinessEvaluator
from super_dev.review_state import (
    architecture_revision_file,
    describe_workflow_event,
    docs_confirmation_file,
    host_runtime_validation_file,
    load_architecture_revision,
    load_docs_confirmation,
    load_host_runtime_validation,
    load_preview_confirmation,
    load_quality_revision,
    load_recent_operational_timeline,
    load_recent_workflow_events,
    load_recent_workflow_snapshots,
    load_ui_revision,
    preview_confirmation_file,
    quality_revision_file,
    save_architecture_revision,
    save_docs_confirmation,
    save_host_runtime_validation,
    save_preview_confirmation,
    save_quality_revision,
    save_ui_revision,
    ui_revision_file,
    workflow_event_log_file,
    workflow_state_file,
)
from super_dev.runtime_evidence import (
    HostRuntimeEvidence,
    IntegrationStatus,
    IntegrationStatusRecord,
    RuntimeStatus,
    RuntimeStatusRecord,
    serialize_host_runtime_evidence,
)
from super_dev.skills import SkillManager
from super_dev.web.rate_limit import RateLimitMiddleware
from super_dev.workflow_contract import get_agent_team, get_workflow_contract
from super_dev.workflow_harness import WorkflowHarnessBuilder
from super_dev.workflow_state import (
    build_host_entry_prompts,
    build_host_flow_contract,
    build_host_flow_probe,
    detect_flow_variant,
    detect_pipeline_summary,
    load_framework_playbook_summary,
    workflow_continuity_rules,
    workflow_mode_label,
    workflow_mode_shortcuts,
)

try:
    import fcntl
except ImportError:
    fcntl = None

_api_logger = logging.getLogger("super_dev.web.api")

# ==================== 路径安全 ====================


def _validate_project_dir(project_dir: str) -> Path:
    """验证项目目录路径，防止路径遍历攻击"""
    segments = project_dir.replace("\\", "/").split("/")
    if ".." in segments:
        raise HTTPException(status_code=400, detail="project_dir 不允许包含 .. 路径遍历")
    normalized = Path(project_dir).resolve()
    return normalized


def _validate_run_id(run_id: str) -> str:
    """验证 run_id，防止路径遍历和注入攻击。

    run_id 只允许字母数字、连字符和下划线。
    """
    if not run_id or not re.match(r"^[a-zA-Z0-9_-]+$", run_id):
        raise HTTPException(
            status_code=400,
            detail="run_id 只允许包含字母、数字、连字符和下划线",
        )
    return run_id


def _public_host_targets(*, integration_manager: IntegrationManager) -> list[str]:
    available_targets = [item.name for item in integration_manager.list_targets()]
    public_targets = [target for target in PRIMARY_HOST_TOOL_IDS if target in available_targets]
    return public_targets or available_targets


# ==================== 数据模型 ====================


class ProjectInitRequest(BaseModel):
    """项目初始化请求"""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=5000)
    platform: str = "web"
    frontend: str = "react"
    backend: str = "node"
    domain: str = ""
    language_preferences: list[str] = []
    quality_gate: int = Field(80, ge=0, le=100)
    host_compatibility_min_score: int = Field(80, ge=0, le=100)
    host_compatibility_min_ready_hosts: int = Field(1, ge=0, le=50)
    host_profile_targets: list[str] = []
    host_profile_enforce_selected: bool = False


class ProjectConfigResponse(BaseModel):
    """项目配置响应"""

    name: str
    description: str
    version: str
    platform: str
    frontend: str
    backend: str
    domain: str
    language_preferences: list[str]
    quality_gate: int
    host_compatibility_min_score: int
    host_compatibility_min_ready_hosts: int
    host_profile_targets: list[str]
    host_profile_enforce_selected: bool
    phases: list[str]
    experts: list[str]


class WorkflowRunRequest(BaseModel):
    """工作流运行请求"""

    phases: list[str] | None = None
    quality_gate: int | None = None
    host_compatibility_min_score: int | None = None
    host_compatibility_min_ready_hosts: int | None = None
    host_profile_targets: list[str] | None = None
    host_profile_enforce_selected: bool | None = None
    language_preferences: list[str] | None = None
    name: str | None = None
    description: str | None = None
    platform: str | None = None
    frontend: str | None = None
    backend: str | None = None
    domain: str | None = None
    cicd: str | None = None
    orm: str | None = None
    offline: bool = False


class WorkflowRunResponse(BaseModel):
    """工作流运行响应"""

    status: str
    message: str
    run_id: str | None = None


class WorkflowDocsConfirmationRequest(BaseModel):
    """文档确认状态更新请求"""

    status: Literal["pending_review", "revision_requested", "confirmed"]
    comment: str = ""
    actor: str = "user"


class WorkflowUIRevisionRequest(BaseModel):
    """UI 改版状态更新请求"""

    status: Literal["pending_review", "revision_requested", "confirmed"]
    comment: str = ""
    actor: str = "user"


class WorkflowPreviewConfirmationRequest(BaseModel):
    """前端预览确认状态更新请求"""

    status: Literal["pending_review", "revision_requested", "confirmed"]
    comment: str = ""
    actor: str = "user"


class WorkflowArchitectureRevisionRequest(BaseModel):
    """架构返工状态更新请求"""

    status: Literal["pending_review", "revision_requested", "confirmed"]
    comment: str = ""
    actor: str = "user"


class WorkflowQualityRevisionRequest(BaseModel):
    """质量返工状态更新请求"""

    status: Literal["pending_review", "revision_requested", "confirmed"]
    comment: str = ""
    actor: str = "user"


class HostRuntimeValidationRequest(BaseModel):
    """宿主真人验收状态更新请求"""

    host: str
    status: Literal["pending", "passed", "failed"]
    comment: str = ""
    actor: str = "user"


class ExpertAdviceRequest(BaseModel):
    """专家建议请求"""

    prompt: str = ""


class DeployGenerateRequest(BaseModel):
    """部署配置生成请求"""

    cicd_platform: str = "all"
    include_runtime: bool = True
    overwrite: bool = True
    name: str | None = None
    platform: str | None = None
    frontend: str | None = None
    backend: str | None = None
    domain: str | None = None


class DeployRemediationExportRequest(BaseModel):
    """部署修复建议导出请求"""

    cicd_platform: str = "all"
    only_missing: bool = True
    split_by_platform: bool = True
    env_file_name: str = ".env.deploy.example"
    checklist_file_name: str | None = None


class PipelinePolicyResponse(BaseModel):
    require_redteam: bool
    require_quality_gate: bool
    require_rehearsal_verify: bool
    min_quality_threshold: int
    allowed_cicd_platforms: list[str]
    require_host_profile: bool
    required_hosts: list[str]
    enforce_required_hosts_ready: bool
    min_required_host_score: int
    policy_file: str
    policy_exists: bool


class PipelinePolicyUpdateRequest(BaseModel):
    preset: str | None = None
    require_redteam: bool | None = None
    require_quality_gate: bool | None = None
    require_rehearsal_verify: bool | None = None
    min_quality_threshold: int | None = None
    allowed_cicd_platforms: list[str] | None = None
    require_host_profile: bool | None = None
    required_hosts: list[str] | None = None
    enforce_required_hosts_ready: bool | None = None
    min_required_host_score: int | None = None


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Super Dev API", description=f"{__description__} - Web API", version=__version__
)

# CORS 配置
_CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-Super-Dev-Key"],
)

app.add_middleware(RateLimitMiddleware)

# ── API Versioning ───────────────────────────────────────
# /api/v1/ is the canonical versioned prefix.
# Legacy /api/ routes remain for backward compatibility but are deprecated.
v1_router = APIRouter(prefix="/api/v1")

# ==================== API Key 认证 ====================

API_KEY_HEADER = APIKeyHeader(name="X-Super-Dev-Key", auto_error=False)


def get_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    """验证 API Key.

    写入端点强制要求 API Key:
    - 如果设置了 SUPER_DEV_API_KEY 环境变量, 则必须提供匹配的 key
    - 如果未设置环境变量, 则生成一次性 key 并写入启动日志 (仅限开发环境)
    - 生产环境必须设置 SUPER_DEV_API_KEY
    """
    expected_key = os.environ.get("SUPER_DEV_API_KEY")
    if not expected_key:
        _generated = os.environ.get("SUPER_DEV_GENERATED_KEY", "")
        if not _generated:
            import secrets

            _generated = secrets.token_urlsafe(32)
            os.environ["SUPER_DEV_GENERATED_KEY"] = _generated
            logging.getLogger("super_dev.web").warning(
                "SUPER_DEV_API_KEY not set. Generated one-time key for this session. "
                "Set SUPER_DEV_API_KEY in production!"
            )
        expected_key = _generated
    if api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_api_key",
                "message": "Valid X-Super-Dev-Key header required. Set SUPER_DEV_API_KEY env var.",
            },
        )
    return api_key


# ==================== 工作流运行状态 ====================

_RUN_STORE: dict[str, dict[str, Any]] = {}
_RUN_STORE_LOCK = Lock()
_RUN_STORE_MAX = 1000


def _evict_run_store() -> None:
    """Evict oldest in-memory run states when store exceeds max size."""
    if len(_RUN_STORE) <= _RUN_STORE_MAX:
        return
    # Remove oldest entries (first N inserted) to stay under limit
    overflow = len(_RUN_STORE) - _RUN_STORE_MAX
    keys_to_remove = list(_RUN_STORE.keys())[:overflow]
    for key in keys_to_remove:
        _RUN_STORE.pop(key, None)


CICDPlatform = Literal["github", "gitlab", "jenkins", "azure", "bitbucket", "all"]
VALID_CICD_PLATFORMS: set[str] = set(CICD_PLATFORM_IDS)
SUPPORTED_BACKEND_TEMPLATES: list[dict[str, str]] = BACKEND_TEMPLATE_CATALOG
SUPPORTED_LANGUAGE_PREFERENCES: list[dict[str, str]] = LANGUAGE_PREFERENCE_CATALOG

_DEPLOY_CICD_FILE_MAP: dict[str, list[str]] = {
    "github": [".github/workflows/ci.yml", ".github/workflows/cd.yml"],
    "gitlab": [".gitlab-ci.yml"],
    "jenkins": ["Jenkinsfile"],
    "azure": [".azure-pipelines.yml"],
    "bitbucket": ["bitbucket-pipelines.yml"],
    "all": [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        ".gitlab-ci.yml",
        "Jenkinsfile",
        ".azure-pipelines.yml",
        "bitbucket-pipelines.yml",
    ],
}

_DEPLOY_RUNTIME_FILES: list[str] = [
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "k8s/deployment.yaml",
    "k8s/service.yaml",
    "k8s/ingress.yaml",
    "k8s/configmap.yaml",
    "k8s/secret.yaml",
]

_DEPLOY_ENV_HINTS: dict[str, list[dict[str, str]]] = {
    "github": [
        {"name": "DOCKER_USERNAME", "description": "Docker 镜像仓库用户名"},
        {"name": "DOCKER_PASSWORD", "description": "Docker 镜像仓库密码/Token"},
        {"name": "KUBE_CONFIG_DEV", "description": "开发环境 Kubernetes kubeconfig"},
        {"name": "KUBE_CONFIG_PROD", "description": "生产环境 Kubernetes kubeconfig"},
    ],
    "gitlab": [
        {"name": "CI_REGISTRY_USER", "description": "GitLab Registry 用户名"},
        {"name": "CI_REGISTRY_PASSWORD", "description": "GitLab Registry 密码/Token"},
        {"name": "KUBE_CONTEXT_DEV", "description": "开发环境 K8s 上下文"},
        {"name": "KUBE_CONTEXT_PROD", "description": "生产环境 K8s 上下文"},
    ],
    "azure": [
        {"name": "AZURE_ACR_SERVICE_CONNECTION", "description": "Azure ACR 服务连接标识"},
        {"name": "AZURE_DEV_K8S_CONNECTION", "description": "开发环境 AKS 服务连接标识"},
        {"name": "AZURE_PROD_K8S_CONNECTION", "description": "生产环境 AKS 服务连接标识"},
    ],
    "bitbucket": [
        {"name": "REGISTRY_URL", "description": "镜像仓库地址"},
        {"name": "KUBE_CONFIG_DEV", "description": "开发环境 Kubernetes kubeconfig"},
        {"name": "KUBE_CONFIG_PROD", "description": "生产环境 Kubernetes kubeconfig"},
    ],
}

_DEPLOY_MANUAL_HINTS: dict[str, list[str]] = {
    "jenkins": [
        "Jenkins Credentials: docker-credentials",
        "Jenkins Credentials: kubeconfig-dev",
        "Jenkins Credentials: kubeconfig-prod",
    ]
}

_DEPLOY_PLATFORM_GUIDANCE: dict[str, list[str]] = {
    "github": [
        "在 GitHub 仓库中打开 Settings > Secrets and variables > Actions。",
        "将必需变量配置为 Repository secrets，并按环境拆分 dev/prod。",
        "首次执行前在 Actions 中手动触发一次 workflow 验证权限。",
    ],
    "gitlab": [
        "在 GitLab 项目中打开 Settings > CI/CD > Variables。",
        "对敏感变量启用 Masked/Protected，并限制到对应分支。",
        "在 Pipeline Editor 先运行 lint 以校验 YAML 语法。",
    ],
    "jenkins": [
        "在 Jenkins 中创建 Credentials（ID 与流水线引用一致）。",
        "确认 Jenkins Agent 具备 Docker 与 kubectl 访问权限。",
        "先在 develop 分支做一次 dry run，再放开生产发布节点。",
    ],
    "azure": [
        "在 Azure DevOps 中创建 Service Connection（ACR + AKS）。",
        "将关键变量放入 Variable Group，并启用 secret 保护。",
        "先运行 Build stage 验证镜像推送权限，再开启 Deploy stage。",
    ],
    "bitbucket": [
        "在 Repository settings > Pipelines > Repository variables 配置变量。",
        "将 kubeconfig 作为 secured variable 保存，避免明文提交。",
        "先对 pull request 流水线执行一次全流程验证。",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_state_dir(project_dir: Path) -> Path:
    return project_dir / ".super-dev" / "runs"


def _run_state_file(project_dir: Path, run_id: str) -> Path:
    return _run_state_dir(project_dir) / f"{run_id}.json"


def _persist_run_state(project_dir: Path, run_id: str, run: dict[str, Any]) -> None:
    state_dir = _run_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    target_file = _run_state_file(project_dir, run_id)
    lock_file = state_dir / ".runs.lock"
    lock_handle = lock_file.open("a+", encoding="utf-8")
    try:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=state_dir,
            prefix=f".{run_id}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_file.write(json.dumps(run, ensure_ascii=False, indent=2))
            temp_path = Path(temp_file.name)
        os.replace(temp_path, target_file)
    finally:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def _load_persisted_run_state(project_dir: Path, run_id: str) -> dict[str, Any] | None:
    file_path = _run_state_file(project_dir, run_id)
    if not file_path.exists():
        return None
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        _api_logger.debug(f"Failed to load persisted run state for {run_id}: {e}")
        return None
    return data if isinstance(data, dict) else None


def _store_run_state(run_id: str, persist_dir: Path | None = None, **fields: Any) -> None:
    with _RUN_STORE_LOCK:
        run = _RUN_STORE.setdefault(run_id, {})
        run.update(fields)
        run["run_id"] = run_id
        run["updated_at"] = _utc_now()
        run["status_normalized"] = _normalize_run_status(run.get("status"))
        if persist_dir is not None:
            _persist_run_state(persist_dir, run_id, run)
        _evict_run_store()


def _get_run_state(run_id: str, project_dir: Path | None = None) -> dict[str, Any] | None:
    with _RUN_STORE_LOCK:
        run = _RUN_STORE.get(run_id)
        if run is not None:
            return dict(run)

    if project_dir is None:
        return None

    persisted = _load_persisted_run_state(project_dir, run_id)
    if persisted is None:
        return None

    with _RUN_STORE_LOCK:
        _RUN_STORE[run_id] = dict(persisted)

    return persisted


def _list_persisted_runs(project_dir: Path, limit: int = 20) -> list[dict[str, Any]]:
    state_dir = _run_state_dir(project_dir)
    if not state_dir.exists():
        return []

    runs: list[dict[str, Any]] = []
    files = sorted(state_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    for file_path in files[:limit]:
        data: dict[str, Any] | None = None
        try:
            loaded = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception as e:
            _api_logger.debug(f"Failed to load persisted run file {file_path.name}: {e}")
            data = None
        if data is not None:
            runs.append(data)
    return runs


def _detect_pipeline_summary(
    project_dir: Path, run: dict[str, Any] | None = None
) -> dict[str, Any]:
    return detect_pipeline_summary(project_dir, run)


def _with_pipeline_summary(run: dict[str, Any], project_dir: Path) -> dict[str, Any]:
    enriched = dict(run)
    enriched["status_normalized"] = _normalize_run_status(enriched.get("status"))
    enriched["pipeline_summary"] = _detect_pipeline_summary(project_dir, run)
    return enriched


def _is_cancel_requested(run_id: str) -> bool:
    with _RUN_STORE_LOCK:
        run = _RUN_STORE.get(run_id)
        return bool(run and run.get("cancel_requested"))


def _normalize_run_status(status: Any) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"success", "completed"}:
        return "completed"
    if normalized in {"failed"}:
        return "failed"
    if normalized in {"cancelled"}:
        return "cancelled"
    if normalized in {
        "running",
        "cancelling",
        "waiting_confirmation",
        "waiting_preview_confirmation",
        "waiting_ui_revision",
        "waiting_architecture_revision",
        "waiting_quality_revision",
    }:
        return "running"
    if normalized in {"queued"}:
        return "queued"
    return "unknown"


def _sanitize_run_payload(value: Any, depth: int = 0) -> Any:
    """将阶段输出裁剪为可安全持久化的 JSON 结构。"""
    if depth > 4:
        return "<truncated>"

    if value is None or isinstance(value, bool | int | float):
        return value

    if isinstance(value, str):
        return value[:500] if len(value) > 500 else value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for idx, (k, v) in enumerate(value.items()):
            if idx >= 80:
                out["__truncated__"] = True
                break
            out[str(k)] = _sanitize_run_payload(v, depth + 1)
        return out

    if isinstance(value, list | tuple | set):
        out_list = []
        for idx, item in enumerate(value):
            if idx >= 120:
                out_list.append("<truncated>")
                break
            out_list.append(_sanitize_run_payload(item, depth + 1))
        return out_list

    return str(value)


def _sanitize_project_name(name: str) -> str:
    sanitized = re.sub(r"[^0-9a-zA-Z_-]+", "-", (name or "").strip()).strip("-")
    return sanitized.lower() or "my-project"


def _display_final_trigger(profile) -> str:
    if getattr(profile, "host", "") == "codex-cli":
        return "App/Desktop: /super-dev | CLI: $super-dev | 回退: super-dev: 你的需求"
    return str(profile.trigger_command).replace("<需求描述>", "你的需求")


def _default_host_commands(host_id: str, *, supports_slash: bool) -> dict[str, str]:
    profile = IntegrationManager(Path.cwd()).get_adapter_profile(host_id)
    trigger = _display_final_trigger(profile)
    skill_name = (
        SkillManager.default_skill_name(host_id)
        if IntegrationManager.requires_skill(host_id)
        else ""
    )
    commands = {
        "setup": f"super-dev setup --host {host_id} --force --yes",
        "onboard": f"super-dev onboard --host {host_id} --force --yes",
        "doctor": f"super-dev doctor --host {host_id} --repair --force",
        "audit": f"super-dev integrate audit --target {host_id}",
        "smoke": f"super-dev integrate smoke --target {host_id}",
        "bugfix": 'super-dev fix "修复当前项目中的关键问题并补充回归验证"',
        "run": 'super-dev "你的需求"',
        "slash": '/super-dev "你的需求"' if supports_slash else "",
        "seeai_slash": '/super-dev-seeai "比赛需求"' if supports_slash else "",
        "skill_slash": "/super-dev" if host_id == "codex-cli" else "",
        "seeai_skill_slash": "/super-dev-seeai" if host_id == "codex-cli" else "",
        "skill": "$super-dev" if host_id == "codex-cli" else skill_name,
        "seeai_skill": "$super-dev-seeai" if host_id == "codex-cli" else "super-dev-seeai",
        "trigger": trigger,
        "seeai_trigger": (
            "App/Desktop: /super-dev-seeai | CLI: $super-dev-seeai | 回退: super-dev-seeai: 比赛需求"
            if host_id == "codex-cli"
            else ('/super-dev-seeai "比赛需求"' if supports_slash else "super-dev-seeai: 比赛需求")
        ),
    }
    return commands


def _competition_mode_payload(host_id: str, *, supports_slash: bool) -> dict[str, Any]:
    contract = get_workflow_contract("seeai")
    if host_id == "codex-cli":
        trigger = "App/Desktop: /super-dev-seeai | CLI: $super-dev-seeai | 回退: super-dev-seeai: 比赛需求"
    elif supports_slash:
        trigger = '/super-dev-seeai "比赛需求"'
    else:
        trigger = "super-dev-seeai: 比赛需求"

    payload: dict[str, Any] = {
        "enabled": True,
        "name": "SEEAI",
        "timebox_minutes": contract.sprint_horizon_minutes,
        "trigger": trigger,
        "phase_chain": [phase.key for phase in contract.phase_chain],
        "agent_team": [agent.key for agent in get_agent_team("seeai")],
        "summary": "比赛快链路：保留 research/三文档/spec，但压缩成半小时内可展示的成品交付。",
        "scope_rule": "先保主路径，再做 wow 点，最后才补额外工程深度。",
        "degrade_rule": "后端或外部集成拖慢节奏时，优先 mock / 本地数据 / 高保真演示流。",
        "first_response_template": [
            "作品类型",
            "评委 wow 点",
            "P0 主路径",
            "主动放弃项",
            "关键假设",
        ],
        "timebox_breakdown": [
            "0-4 分钟：fast research",
            "4-8 分钟：compact 文档",
            "8-10 分钟：docs confirm",
            "10-12 分钟：compact spec",
            "12-27 分钟：full-stack sprint",
            "27-30 分钟：polish/handoff",
        ],
        "archetype_detection_hints": [
            "品牌、官网、落地页、活动宣传、首屏 -> 官网类",
            "玩法、得分、胜负、闯关、点击反馈 -> 小游戏类",
            "生成、分析、查询、输入输出、结果页、效率提升 -> 工具类",
        ],
        "compact_doc_sections": {
            "research": ["题目理解", "参考风格", "Wow 点", "主动放弃项"],
            "prd": ["作品目标", "P0 主路径", "P1 Wow 点", "P2 可选项", "非目标"],
            "architecture": ["主循环", "技术栈", "数据流", "最小后端", "降级方案"],
            "uiux": ["视觉方向", "首屏/主界面", "关键交互", "动效重点", "设计 Token"],
            "spec": ["P0", "P1", "Polish"],
        },
        "quality_floor": list(contract.quality_floor),
        "archetype_playbooks": {
            "landing_page": {
                "label": "官网类",
                "default_stack": "React/Vite 或 Next.js + Tailwind + Framer Motion",
                "sprint_plan": ["Hero/首屏", "亮点区/品牌叙事", "CTA/滚动动效", "最终 polish"],
                "focus": "主视觉、信息密度、滚动节奏、首屏转化",
            },
            "mini_game": {
                "label": "小游戏类",
                "default_stack": "HTML Canvas + Vanilla JS；复杂玩法再上 Phaser",
                "sprint_plan": ["主循环可玩", "积分/胜负反馈", "特效/音效", "复玩和 polish"],
                "focus": "玩法闭环、反馈感、积分胜负、再次游玩",
            },
            "tool": {
                "label": "工具类",
                "default_stack": "React + Vite + Tailwind；必要时补最小 Express/Fastify 后端",
                "sprint_plan": ["输入页/主流程", "结果页", "分享/导出", "最终 polish"],
                "focus": "高价值主流程、输入输出清晰、结果页直观",
            },
        },
        "host_tips": [],
    }

    if host_id in {"codebuddy", "codebuddy-cli"}:
        payload["host_tips"] = [
            "固定在同一个项目上下文会话里完成比赛冲刺，减少子会话切换。",
            "如果 slash 列表刷新慢，直接回退到 super-dev-seeai: 继续。",
            "按 P0/P1/P2 控制范围，先保住主演示路径。",
        ]
    elif host_id == "openclaw":
        payload["host_tips"] = [
            "安装插件后优先新开一个绑定当前项目的 Agent 会话。",
            "如果 /super-dev-seeai 尚未出现在命令面板，直接使用 super-dev-seeai:。",
            "中段优先做主作品，末段再调用 Tool 做质量与状态收口。",
        ]
    else:
        payload["host_tips"] = [
            "先保住一个可演示主路径，再补一个明显 wow 点。",
            "真实后端来不及时，优先用 mock / 本地数据保持演示完整。",
        ]

    return payload


def _build_host_tool_catalog_payload() -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for item in HOST_TOOL_CATALOG:
        host_id = item["id"]
        target = IntegrationManager.TARGETS.get(host_id)
        supports_slash = IntegrationManager.supports_slash(host_id)
        profile = IntegrationManager(Path.cwd()).get_adapter_profile(host_id)
        final_trigger = _display_final_trigger(profile)
        payload.append(
            {
                "id": host_id,
                "name": item["name"],
                "category": HOST_TOOL_CATEGORY_MAP.get(host_id, "ide"),
                "install_mode": (
                    get_install_mode(host_id).value if get_install_mode(host_id) is not None else ""
                ),
                "certification_level": profile.certification_level,
                "certification_label": profile.certification_label,
                "certification_reason": profile.certification_reason,
                "certification_evidence": list(profile.certification_evidence),
                "host_protocol_mode": profile.host_protocol_mode,
                "host_protocol_summary": profile.host_protocol_summary,
                "official_docs_url": profile.official_docs_url,
                "docs_verified": profile.docs_verified,
                "integration_files": list(target.files) if target else [],
                "official_project_surfaces": list(profile.official_project_surfaces),
                "official_user_surfaces": list(profile.official_user_surfaces),
                "optional_project_surfaces": list(profile.optional_project_surfaces),
                "optional_user_surfaces": list(profile.optional_user_surfaces),
                "observed_compatibility_surfaces": list(profile.observed_compatibility_surfaces),
                "slash_command_file": (
                    IntegrationManager.SLASH_COMMAND_FILES.get(host_id, "")
                    if supports_slash
                    else ""
                ),
                "supports_slash": supports_slash,
                "usage_mode": profile.usage_mode,
                "primary_entry": profile.primary_entry,
                "final_trigger": final_trigger,
                "entry_variants": list(profile.entry_variants),
                "trigger_context": profile.trigger_context,
                "usage_location": profile.usage_location,
                "requires_restart_after_onboard": profile.requires_restart_after_onboard,
                "post_onboard_steps": list(profile.post_onboard_steps),
                "usage_notes": list(profile.usage_notes),
                "smoke_test_prompt": profile.smoke_test_prompt,
                "smoke_test_steps": list(profile.smoke_test_steps),
                "smoke_success_signal": profile.smoke_success_signal,
                "competition_smoke_test_prompt": profile.competition_smoke_test_prompt,
                "competition_smoke_test_steps": list(profile.competition_smoke_test_steps),
                "competition_smoke_success_signal": profile.competition_smoke_success_signal,
                "supports_skill_slash_entry": host_id == "codex-cli",
                "skill_slash_entry_command": "/super-dev" if host_id == "codex-cli" else "",
                "skill_slash_entry_note": (
                    "Indicates the enabled Skill entry shown in the Codex app slash list, not a project-level custom slash command."
                    if host_id == "codex-cli"
                    else ""
                ),
                "flow_contract": build_host_flow_contract(host_id),
                "flow_probe": build_host_flow_probe(host_id),
                "competition_mode": _competition_mode_payload(
                    host_id, supports_slash=supports_slash
                ),
                "notes": profile.notes,
                "commands": _default_host_commands(host_id, supports_slash=supports_slash),
            }
        )
    return payload


def _detect_host_targets(available_targets: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    detected: list[str] = []
    details: dict[str, list[str]] = {}
    for target in available_targets:
        reasons: list[str] = []
        for command in HOST_COMMAND_CANDIDATES.get(target, []):
            if shutil.which(command):
                reasons.append(f"cmd:{command}")
                break

        for source, candidate in host_detection_path_candidates(target):
            if glob.glob(candidate):
                reasons.append(f"{source}:{candidate}")
                break

        if reasons:
            detected.append(target)
            details[target] = reasons
    return detected, details


def _format_detection_reason(reason: str) -> str:
    source, _, value = str(reason).partition(":")
    source_labels = {
        "cmd": "命令命中",
        "path": "默认安装路径",
        "env": "自定义路径覆盖",
        "registry": "Windows 注册信息",
        "shim": "Windows shim / 包管理器目录",
    }
    label = source_labels.get(source, source or "检测来源")
    return f"{label}: {value}" if value else label


def _explain_detection_details(detected_meta: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        host: [_format_detection_reason(item) for item in reasons]
        for host, reasons in detected_meta.items()
    }


def _host_runtime_checklist(
    target: str, usage: dict[str, Any], project_dir: Path | None = None
) -> list[str]:
    trigger = str(usage.get("final_trigger", "")).strip() or "-"
    common = [
        f"在宿主中使用最终触发命令进入 Super Dev 流水线：{trigger}",
        "确认首轮响应明确进入 research，而不是直接开始编码。",
        "确认真实写入 output/*-research.md、output/*-prd.md、output/*-architecture.md、output/*-uiux.md。",
        "确认三文档完成后暂停等待用户确认，而不是直接继续实现。",
        "确认文档确认后能继续进入 Spec、前端运行验证、后端与交付阶段。",
    ]
    if project_dir is not None:
        framework_playbook = load_framework_playbook_summary(project_dir)
        if framework_playbook:
            common.extend(
                [
                    f"确认当前项目按 {framework_playbook.get('framework', '跨平台框架')} playbook 执行，而不是按普通 Web 假设实现。",
                    "确认宿主已落实框架专项原生能力面，而不是只完成通用页面实现。",
                    "确认宿主已按框架专项必验场景完成真实验证，并沉淀交付证据。",
                ]
            )
    overrides = host_runtime_validation_overrides(target)
    return [*overrides.get("runtime_checklist", []), *common]


def _host_runtime_pass_criteria(target: str, project_dir: Path | None = None) -> list[str]:
    common = [
        "首轮响应符合 Super Dev 首轮契约。",
        "关键文档真实落盘到项目目录。",
        "确认门真实生效。",
        "后续恢复路径可用。",
    ]
    if project_dir is not None and load_framework_playbook_summary(project_dir):
        common.append("跨平台框架专项能力、必验场景与交付证据均已通过真人验收。")
    overrides = host_runtime_validation_overrides(target)
    return [*overrides.get("pass_criteria", []), *common]


def _project_has_super_dev_context(project_dir: Path) -> bool:
    project_dir = Path(project_dir).resolve()
    return any(
        path.exists()
        for path in (
            project_dir / "super-dev.yaml",
            project_dir / ".super-dev" / "WORKFLOW.md",
            project_dir / "output" / f"{project_dir.name}-prd.md",
            project_dir / "output" / f"{project_dir.name}-architecture.md",
            project_dir / "output" / f"{project_dir.name}-proof-pack.json",
        )
    )


def _build_resume_probe_instruction(project_dir: Path) -> str:
    if not _project_has_super_dev_context(project_dir):
        return ""
    return (
        "继续当前项目的 Super Dev 流程，不要当作普通聊天。"
        "先读取 .super-dev/SESSION_BRIEF.md、.super-dev/workflow-state.json、.super-dev/WORKFLOW.md、output/*、.super-dev/review-state/* 和最近的 tasks.md。"
    )


def _build_resume_probe_prompt(project_dir: Path, target: str, usage: dict[str, Any]) -> str:
    instruction = _build_resume_probe_instruction(project_dir)
    if not instruction:
        return ""
    trigger = str(usage.get("trigger_command", "")).strip()
    flow_variant = detect_flow_variant(project_dir)
    entry_bundle = build_host_entry_prompts(
        target=target,
        instruction=instruction,
        supports_slash=bool("/super-dev" in trigger),
        flow_variant=flow_variant,
    )
    preferred_entry = str(entry_bundle.get("preferred_entry", "")).strip()
    prompts = entry_bundle.get("entry_prompts", {})
    if isinstance(prompts, dict) and preferred_entry:
        prompt = str(prompts.get(preferred_entry, "")).strip()
        if prompt:
            return prompt
    return f"super-dev: {instruction}"


def _host_resume_checklist(target: str, project_dir: Path | None = None) -> list[str]:
    common = [
        "重开宿主或新开会话后，使用恢复探针而不是普通闲聊进入当前流程。",
        "确认宿主先读取 `.super-dev/SESSION_BRIEF.md`，并继续当前流程而不是重新开始。",
        "确认用户继续说“改一下 / 补充 / 继续改 / 确认 / 通过”时，宿主仍然留在当前 Super Dev 流程内。",
    ]
    if project_dir is not None:
        framework_playbook = load_framework_playbook_summary(project_dir)
        if framework_playbook:
            common.append(
                f"恢复后继续实现或返工时，仍然遵守 {framework_playbook.get('framework', '跨平台框架')} 的专项 playbook。"
            )
    overrides = host_runtime_validation_overrides(target)
    return [*overrides.get("resume_checklist", []), *common]


def _build_session_resume_card(
    project_dir: Path, target: str, usage: dict[str, Any]
) -> dict[str, Any]:
    host_first_sentence = _build_resume_probe_prompt(project_dir, target, usage)
    instruction = _build_resume_probe_instruction(project_dir)
    enabled = bool(host_first_sentence)
    workflow_mode = ""
    workflow_mode_display = ""
    action_title = ""
    action_examples: list[str] = []
    rules: list[str] = []
    recommended_workflow_command = ""
    entry_prompts: dict[str, str] = {}
    preferred_entry = ""
    preferred_entry_label = ""
    summary: dict[str, Any] = {}
    if enabled:
        summary = _detect_pipeline_summary(project_dir)
        entry_bundle = build_host_entry_prompts(
            target=target,
            instruction=instruction,
            supports_slash=bool("/super-dev" in str(usage.get("trigger_command", "")).strip()),
            flow_variant=str(summary.get("flow_variant", "")).strip()
            or detect_flow_variant(project_dir),
        )
        raw_entry_prompts = entry_bundle.get("entry_prompts", {})
        if isinstance(raw_entry_prompts, dict):
            entry_prompts = {
                str(key): str(value).strip()
                for key, value in raw_entry_prompts.items()
                if str(value).strip()
            }
        preferred_entry = str(entry_bundle.get("preferred_entry", "")).strip()
        preferred_entry_label = str(entry_bundle.get("preferred_entry_label", "")).strip()
        recommended_workflow_command = (
            str(summary.get("recommended_command", "")).strip() or "在宿主里说“继续当前流程”"
        )
        workflow_mode = str(summary.get("workflow_mode", "")).strip()
        if workflow_mode:
            workflow_mode_display = workflow_mode_label(workflow_mode)
        action_card = summary.get("action_card")
        if isinstance(action_card, dict):
            action_title = str(action_card.get("title", "")).strip()
            raw_examples = action_card.get("examples")
            if isinstance(raw_examples, list):
                action_examples = [str(item).strip() for item in raw_examples if str(item).strip()]
            raw_rules = action_card.get("continuity_rules")
            if isinstance(raw_rules, list):
                rules = [str(item).strip() for item in raw_rules if str(item).strip()]
            raw_shortcuts = action_card.get("shortcuts")
            if isinstance(raw_shortcuts, list):
                user_action_shortcuts = [
                    str(item).strip() for item in raw_shortcuts if str(item).strip()
                ]
            else:
                user_action_shortcuts = workflow_mode_shortcuts(
                    workflow_mode, examples=action_examples
                )
        else:
            user_action_shortcuts = workflow_mode_shortcuts(workflow_mode)
        if not rules:
            rules = workflow_continuity_rules(str(summary.get("workflow_status", "")).strip())
    else:
        user_action_shortcuts = []
    session_brief_path = (
        str((project_dir / ".super-dev" / "SESSION_BRIEF.md").resolve()) if enabled else ""
    )
    workflow_state_path = str(workflow_state_file(project_dir).resolve()) if enabled else ""
    framework_playbook = load_framework_playbook_summary(project_dir) if enabled else {}
    recent_snapshots = load_recent_workflow_snapshots(project_dir, limit=3) if enabled else []
    recent_events = load_recent_workflow_events(project_dir, limit=3) if enabled else []
    recent_hook_events = HookManager.load_recent_history(project_dir, limit=3) if enabled else []
    recent_timeline = load_recent_operational_timeline(project_dir, limit=5) if enabled else []
    harness_summaries = (
        summarize_operational_harnesses(project_dir, write_reports=False) if enabled else []
    )
    operational_focus = derive_operational_focus(project_dir) if enabled else {}
    scenario_cards = list(summary.get("scenario_cards") or []) if enabled else []
    lines = []
    if enabled:
        generic_continue_rule = (
            "用户说“改一下 / 补充 / 继续改 / 确认 / 通过”时，仍然留在当前 Super Dev 流程。"
        )
        generic_exit_rule = "只有用户明确说取消当前流程、重新开始或切回普通聊天，才允许离开流程。"
        primary_rule = str(rules[0]).strip() if rules else ""
        exit_rule = str(rules[1]).strip() if len(rules) > 1 else ""
        lines = [
            f"动作类型: {workflow_mode_display}" if workflow_mode_display else "",
            f"当前动作: {action_title}" if action_title else "",
            f"宿主第一句: {host_first_sentence}",
            f"流程状态卡: {session_brief_path}",
            f"工作流状态 JSON: {workflow_state_path}",
            f"继续规则: {generic_continue_rule}",
            (
                f"当前门禁规则: {primary_rule}"
                if primary_rule and primary_rule != generic_continue_rule
                else ""
            ),
            f"退出条件: {generic_exit_rule}",
            (
                f"当前门禁退出条件: {exit_rule}"
                if exit_rule and exit_rule != generic_exit_rule
                else ""
            ),
        ]
        if framework_playbook:
            lines.append(f"框架专项: {framework_playbook.get('framework', '-')}")
            native = framework_playbook.get("native_capabilities", [])
            validation = framework_playbook.get("validation_surfaces", [])
            if native:
                lines.append(f"原生能力面: {' / '.join(str(item) for item in native[:3])}")
            if validation:
                lines.append(f"必验场景: {' / '.join(str(item) for item in validation[:3])}")
        if recent_snapshots:
            first = recent_snapshots[0]
            step = (
                str(first.get("current_step_label", "")).strip()
                or str(first.get("status", "")).strip()
            )
            updated_at = str(first.get("updated_at", "")).strip() or "-"
            lines.append(f"最近一次: {updated_at} · {step}")
        if recent_events:
            latest_event = recent_events[0]
            event_time = str(latest_event.get("timestamp", "")).strip() or "-"
            lines.append(f"最近事件: {event_time} · {describe_workflow_event(latest_event)}")
        if recent_hook_events:
            latest_hook = recent_hook_events[0]
            hook_status = (
                "blocked" if latest_hook.blocked else ("ok" if latest_hook.success else "failed")
            )
            lines.append(
                f"最近 Hook: {latest_hook.timestamp} · {latest_hook.event} / {latest_hook.phase or '-'} / {latest_hook.hook_name} / {hook_status}"
            )
        if recent_timeline:
            latest_timeline = recent_timeline[0]
            timeline_time = str(latest_timeline.get("timestamp", "")).strip() or "-"
            timeline_title = (
                str(latest_timeline.get("title", "")).strip()
                or str(latest_timeline.get("kind", "")).strip()
            )
            timeline_message = str(latest_timeline.get("message", "")).strip() or "-"
            lines.append(f"关键时间线: {timeline_time} · {timeline_title} · {timeline_message}")
        if harness_summaries:
            for item in harness_summaries[:3]:
                label = str(item.get("label", "")).strip() or str(item.get("kind", "")).strip()
                status = "pass" if item.get("passed") else "fail"
                line = f"{label}: {status}"
                blocker = str(item.get("first_blocker", "")).strip()
                if blocker:
                    line += f" · {blocker}"
                lines.append(line)
        focus_summary = str(operational_focus.get("summary", "")).strip()
        focus_action = str(operational_focus.get("recommended_action", "")).strip()
        if focus_summary:
            lines.append(f"当前治理焦点: {focus_summary}")
        if focus_action:
            lines.append(f"建议先做: {focus_action}")
        if user_action_shortcuts:
            lines.insert(2, f"你现在可以直接说: {' / '.join(user_action_shortcuts[:4])}")
        if action_examples:
            lines.insert(
                3 if user_action_shortcuts else 2, f"自然语言示例: {', '.join(action_examples[:3])}"
            )
        if scenario_cards:
            insert_at = (
                4
                if user_action_shortcuts and action_examples
                else 3 if (user_action_shortcuts or action_examples) else 2
            )
            scenario_lines = []
            for item in scenario_cards[:4]:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", "")).strip()
                command = str(item.get("cli_command", "")).strip()
                if title and command:
                    scenario_lines.append(f"真实场景: {title} -> {command}")
            for offset, line in enumerate(scenario_lines):
                lines.insert(insert_at + offset, line)
        if recommended_workflow_command:
            lines.append(f"系统建议动作: {recommended_workflow_command}")
        lines = [line for line in lines if line]
    return {
        "enabled": enabled,
        "host_first_sentence": host_first_sentence,
        "preferred_entry": preferred_entry if enabled else "",
        "preferred_entry_label": preferred_entry_label if enabled else "",
        "entry_prompts": entry_prompts if enabled else {},
        "session_brief_path": session_brief_path,
        "workflow_state_path": workflow_state_path,
        "workflow_event_log_path": (
            str(workflow_event_log_file(project_dir).resolve()) if enabled else ""
        ),
        "hook_history_path": (
            str(HookManager.hook_history_file(project_dir).resolve()) if enabled else ""
        ),
        "framework_playbook": framework_playbook if enabled else {},
        "operational_harnesses": harness_summaries if enabled else [],
        "operational_focus": operational_focus if enabled else {},
        "recent_snapshots": recent_snapshots if enabled else [],
        "recent_events": recent_events if enabled else [],
        "recent_hook_events": [item.to_dict() for item in recent_hook_events] if enabled else [],
        "recent_timeline": recent_timeline if enabled else [],
        "workflow_mode": workflow_mode if enabled else "",
        "workflow_mode_label": workflow_mode_display if enabled else "",
        "flow_variant": str(summary.get("flow_variant", "")).strip() if enabled else "",
        "action_title": action_title if enabled else "",
        "action_examples": action_examples if enabled else [],
        "user_action_shortcuts": user_action_shortcuts if enabled else [],
        "scenario_cards": scenario_cards if enabled else [],
        "rules": (
            [
                generic_continue_rule,
                *[str(item).strip() for item in rules if str(item).strip()],
                generic_exit_rule,
            ]
            if enabled
            else []
        ),
        "recommended_workflow_command": recommended_workflow_command,
        "lines": lines,
    }


def _build_no_host_decision_card() -> dict[str, Any]:
    next_actions = [
        "先安装一个受支持宿主，优先 Claude Code 或 Codex。",
        "如果宿主装在自定义目录，先设置对应的 SUPER_DEV_HOST_PATH_* 环境变量。",
        "安装后先执行 detect / doctor，再开始接入。",
    ]
    first_action = next_actions[0]
    return {
        "scenario": "no-host-detected",
        "workflow_mode": "start",
        "workflow_mode_label": workflow_mode_label("start"),
        "action_title": "先完成宿主安装与接入",
        "action_examples": ["先装 Codex", "我先用 Claude Code", "先把宿主接好再开始"],
        "user_action_shortcuts": workflow_mode_shortcuts(
            "start", examples=["先装 Codex", "我先用 Claude Code", "先把宿主接好再开始"]
        ),
        "title": "未检测到可用宿主",
        "summary": "当前机器上没有命中受支持宿主，或宿主不在默认路径与当前 PATH 中。",
        "recommended_reason": "先保证机器上至少有一个正式支持的宿主可用，再进入接入流程。",
        "first_action": first_action,
        "secondary_actions": next_actions[1:],
        "path_override_hint": "如果装在自定义目录，先设置 `SUPER_DEV_HOST_PATH_CODEX_CLI=<安装路径>` 这类环境变量再重试。",
        "path_override_examples": [
            {
                "id": host_id,
                "name": host_display,
                "env_key": str(host_path_override_guide(host_id).get("env_key", "")),
                "unix_example": str(host_path_override_guide(host_id).get("unix_example", "")),
                "windows_example": str(
                    host_path_override_guide(host_id).get("windows_example", "")
                ),
            }
            for host_id, host_display in (("claude-code", "Claude Code"), ("codex-cli", "Codex"))
        ],
        "next_actions": next_actions,
        "lines": [
            f"动作类型: {workflow_mode_label('start')}",
            "当前动作: 先完成宿主安装与接入",
            f"先做这一步: {first_action}",
            "当前机器上未命中受支持宿主。",
            "如果装在自定义目录，先设置 `SUPER_DEV_HOST_PATH_CODEX_CLI=<安装路径>` 这类环境变量再重试。",
            "自然语言示例: 先装 Codex, 我先用 Claude Code, 先把宿主接好再开始",
        ],
    }


def _build_detected_host_decision_card(
    *,
    project_dir: Path,
    integration_manager: IntegrationManager,
    detected_targets: list[str],
    detected_meta: dict[str, list[str]],
    preferred_targets: list[str] | None = None,
) -> dict[str, Any]:
    candidate_targets = list(dict.fromkeys([*(preferred_targets or []), *detected_targets]))
    if not candidate_targets:
        return _build_no_host_decision_card()
    candidate_display_limit = 3

    def _sort_key(target: str) -> tuple[int, int, int, str]:
        profile = integration_manager.get_adapter_profile(target)
        certification_rank = (
            0
            if profile.certification_level == "certified"
            else (1 if profile.certification_level == "compatible" else 2)
        )
        return (
            certification_rank,
            0 if integration_manager.supports_slash(target) else 1,
            0 if profile.category == "cli" else 1,
            target,
        )

    ranked_targets = sorted(candidate_targets, key=_sort_key)
    preferred_set = {target for target in (preferred_targets or []) if target}
    if preferred_set:
        ranked_targets = sorted(
            ranked_targets,
            key=lambda target: (0 if target in preferred_set else 1, ranked_targets.index(target)),
        )
    selected_host = ranked_targets[0]
    usage = _serialize_host_usage_profile(
        integration_manager=integration_manager, target=selected_host
    )
    session_resume_card = _build_session_resume_card(project_dir, selected_host, usage)
    selected_profile = integration_manager.get_adapter_profile(selected_host)
    if selected_profile.certification_level == "certified" and integration_manager.supports_slash(
        selected_host
    ):
        recommended_reason = "它当前是已检测宿主里认证等级最高、触发入口最直接的一项。"
    elif selected_profile.certification_level == "certified":
        recommended_reason = "它当前是已检测宿主里认证等级最高的一项。"
    elif integration_manager.supports_slash(selected_host):
        recommended_reason = "它当前触发入口最直接，适合作为默认宿主。"
    else:
        recommended_reason = "它当前在已检测宿主里综合优先级最高。"
    first_action = (
        f"重开后第一句直接复制 {session_resume_card.get('host_first_sentence')}"
        if session_resume_card.get("enabled")
        else (
            "先在 Codex App/Desktop 的 `/` 列表里选择 `super-dev`，或在 Codex CLI 输入 `$super-dev`；自然语言回退是 `super-dev: 你的需求`"
            if selected_host == "codex-cli"
            else f"先在 {usage['host']} 里输入 {str(selected_profile.trigger_command).replace('<需求描述>', '你的需求')}"
        )
    )
    workflow_mode = "continue" if session_resume_card.get("enabled") else "start"
    action_title = (
        str(session_resume_card.get("action_title", "")).strip()
        if session_resume_card.get("enabled")
        else f"在 {usage['host']} 里启动 Super Dev"
    )
    action_examples = (
        list(session_resume_card.get("action_examples") or [])
        if session_resume_card.get("enabled")
        else ["开始这个项目", "做一个商业级官网", "用 Super Dev 开始处理当前需求"]
    )
    user_action_shortcuts = workflow_mode_shortcuts(workflow_mode, examples=action_examples)
    candidates: list[dict[str, Any]] = []
    for target in ranked_targets:
        candidate_usage = _serialize_host_usage_profile(
            integration_manager=integration_manager, target=target
        )
        profile = integration_manager.get_adapter_profile(target)
        if profile.certification_level == "certified" and integration_manager.supports_slash(
            target
        ):
            candidate_reason = "它当前是已检测宿主里认证等级最高、触发入口最直接的一项。"
        elif profile.certification_level == "certified":
            candidate_reason = "它当前是已检测宿主里认证等级最高的一项。"
        elif integration_manager.supports_slash(target):
            candidate_reason = "它当前触发入口最直接，适合作为默认宿主。"
        else:
            candidate_reason = "它当前在已检测宿主里综合优先级最高。"
        candidates.append(
            {
                "id": target,
                "name": candidate_usage["host"],
                "certification_label": profile.certification_label,
                "certification_level": profile.certification_level,
                "recommended": target == selected_host,
                "recommended_reason": candidate_reason,
                "reasons": _explain_detection_details({target: detected_meta.get(target, [])}).get(
                    target, []
                ),
                "trigger": (
                    "Codex App/Desktop: `/super-dev`；Codex CLI: `$super-dev`；回退: `super-dev: 你的需求`"
                    if target == "codex-cli"
                    else str(profile.trigger_command).replace("<需求描述>", "你的需求")
                ),
                "path_override": host_path_override_guide(target),
            }
        )
    display_candidates = candidates[:candidate_display_limit]
    remaining_candidate_count = max(0, len(candidates) - len(display_candidates))
    secondary_actions = [
        "如果当前是重开宿主后的第一轮输入，先不要普通聊天起手，直接用建议入口。",
        "如果命令或技能还没刷新，先关闭旧宿主会话再开新会话。",
    ]
    selection_source = "explicit" if preferred_set else "detected"
    lines = [
        f"动作类型: {workflow_mode_label(workflow_mode)}",
        f"当前动作: {action_title}",
        f"先做这一步: {first_action}",
        f"默认推荐先用 {usage['host']}，{recommended_reason}",
        f"当前建议入口: {usage['primary_entry']}",
    ]
    if selection_source == "explicit":
        lines.insert(3, f"当前模式: 仅围绕 {usage['host']} 给出建议。")
    if action_examples:
        lines.append(f"自然语言示例: {', '.join(str(item) for item in action_examples[:3])}")
    candidate_summary = "、".join(
        f"{item['name']} [{item['certification_label']}]" for item in display_candidates
    )
    if candidate_summary:
        lines.append(f"优先候选: {candidate_summary}")
    if remaining_candidate_count:
        lines.append(f"另外还有 {remaining_candidate_count} 个候选已折叠，默认不建议先看。")
    if session_resume_card.get("enabled"):
        lines.append(f"继续当前流程第一句: {session_resume_card.get('host_first_sentence')}")
    elif candidates:
        lines.append(f"第一句建议: {candidates[0]['trigger']}")
    return {
        "scenario": "multi-host-detected" if len(candidate_targets) > 1 else "single-host-detected",
        "selection_source": selection_source,
        "workflow_mode": workflow_mode,
        "workflow_mode_label": workflow_mode_label(workflow_mode),
        "action_title": action_title,
        "action_examples": action_examples,
        "user_action_shortcuts": user_action_shortcuts,
        "title": "已检测到宿主",
        "summary": (
            f"当前已按你指定的宿主给出默认建议，共纳入 {len(candidate_targets)} 个候选。"
            if selection_source == "explicit"
            else f"当前检测到 {len(detected_targets)} 个宿主，已按优先级给出默认推荐。"
        ),
        "recommended_reason": recommended_reason,
        "first_action": first_action,
        "secondary_actions": secondary_actions,
        "selected_host": selected_host,
        "selected_host_name": usage["host"],
        "selected_path_override": host_path_override_guide(selected_host),
        "candidate_count": len(candidates),
        "remaining_candidate_count": remaining_candidate_count,
        "candidates": display_candidates,
        "session_resume_card": session_resume_card,
        "lines": lines,
    }


def _build_primary_repair_action(
    *,
    report: dict[str, Any],
    targets: list[str],
    integration_manager: IntegrationManager,
    decision_card: dict[str, Any] | None = None,
) -> dict[str, Any]:
    hosts = report.get("hosts", {})
    if isinstance(decision_card, dict) and decision_card.get("scenario") == "no-host-detected":
        first_action = str(decision_card.get("first_action", "")).strip()
        if first_action:
            secondary_actions = decision_card.get("secondary_actions", [])
            return {
                "host": "当前机器",
                "reason": str(decision_card.get("summary", "")).strip(),
                "command": first_action,
                "secondary_actions": (
                    secondary_actions if isinstance(secondary_actions, list) else []
                ),
            }
    if not isinstance(hosts, dict):
        return {"host": "", "reason": "", "command": "", "secondary_actions": []}
    for target in targets:
        host = hosts.get(target, {})
        if not isinstance(host, dict) or bool(host.get("ready", False)):
            continue
        diagnosis = host.get("diagnosis", {})
        if not isinstance(diagnosis, dict):
            continue
        command = str(diagnosis.get("suggested_command", "")).strip()
        if not command:
            continue
        reason = str(diagnosis.get("blocker_summary", "")).strip()
        suggestions = host.get("suggestions", [])
        secondary_actions: list[str] = []
        if isinstance(suggestions, list):
            for item in suggestions:
                text = str(item).strip()
                if not text or text == command or text in secondary_actions:
                    continue
                secondary_actions.append(text)
                if len(secondary_actions) >= 2:
                    break
        return {
            "host": _serialize_host_usage_profile(
                integration_manager=integration_manager, target=target
            )["host"],
            "reason": reason,
            "command": command,
            "secondary_actions": secondary_actions,
        }
    return {"host": "", "reason": "", "command": "", "secondary_actions": []}


def _collect_host_diagnostics(
    *,
    project_dir: Path,
    targets: list[str],
    skill_name: str,
    check_integrate: bool,
    check_skill: bool,
    check_slash: bool,
) -> dict[str, Any]:
    integration_manager = IntegrationManager(project_dir)

    report: dict[str, Any] = {"hosts": {}, "overall_ready": True}
    for target in targets:
        host_report: dict[str, Any] = {
            "ready": True,
            "checks": {},
            "missing": [],
            "optional_missing": [],
            "suggestions": [],
        }
        surface_groups = integration_manager.readiness_surface_sets(
            target=target,
            skill_name=skill_name,
        )
        surface_classification = integration_manager.managed_surface_classification(
            target=target,
            skill_name=skill_name,
        )

        surface_audit: dict[str, dict[str, Any]] = {}
        for surface_key, surface_path in integration_manager.collect_managed_surface_paths(
            target=target,
            skill_name=skill_name,
        ).items():
            surface_meta = surface_classification.get(surface_key, {})
            exists = surface_path.exists()
            audit_entry: dict[str, Any] = {
                "path": str(surface_path),
                "exists": exists,
                "group": str(surface_meta.get("group", "unclassified")),
                "required": bool(surface_meta.get("required", False)),
                "missing_markers": [],
            }
            if exists:
                try:
                    content = surface_path.read_text(encoding="utf-8")
                except Exception as exc:
                    audit_entry["read_error"] = str(exc)
                    audit_entry["missing_markers"] = ["unreadable"]
                else:
                    audit_entry["missing_markers"] = integration_manager.audit_surface_contract(
                        target,
                        surface_key,
                        surface_path,
                        content,
                    )
            surface_audit[surface_key] = audit_entry

        invalid_required_surfaces = {
            key: value
            for key, value in surface_audit.items()
            if value.get("exists") and value.get("required") and value.get("missing_markers")
        }
        invalid_optional_surfaces = {
            key: value
            for key, value in surface_audit.items()
            if value.get("exists") and not value.get("required") and value.get("missing_markers")
        }
        host_report["checks"]["contract"] = {
            "ok": not invalid_required_surfaces,
            "surfaces": surface_audit,
            "invalid_surfaces": invalid_required_surfaces,
            "invalid_optional_surfaces": invalid_optional_surfaces,
        }
        if invalid_required_surfaces:
            host_report["ready"] = False
            host_report["missing"].append("contract")
            host_report["suggestions"].append(f"super-dev onboard --host {target} --force --yes")
        if invalid_optional_surfaces:
            host_report["optional_missing"].append("contract_optional_surfaces")

        if check_integrate:
            integrate_files = surface_groups["official_project"]
            optional_integrate_files = surface_groups["optional_project"]
            integrate_ok = all(path.exists() for path in integrate_files)
            host_report["checks"]["integrate"] = {
                "ok": integrate_ok,
                "files": [str(item) for item in integrate_files],
                "optional_files": [str(item) for item in optional_integrate_files],
            }
            if not integrate_ok:
                host_report["ready"] = False
                host_report["missing"].append("integrate")
                host_report["suggestions"].append(
                    f"super-dev integrate setup --target {target} --force"
                )
            user_surface_files = surface_groups["official_user"]
            optional_user_surface_files = surface_groups["optional_user"]
            user_surfaces_ok = all(path.exists() for path in user_surface_files)
            host_report["checks"]["user_surfaces"] = {
                "ok": user_surfaces_ok,
                "files": [str(item) for item in user_surface_files],
                "optional_files": [str(item) for item in optional_user_surface_files],
            }
            if user_surface_files and not user_surfaces_ok:
                host_report["ready"] = False
                host_report["missing"].append("user_surfaces")
                host_report["suggestions"].append(
                    f"super-dev onboard --host {target} --force --yes"
                )

        if check_skill and IntegrationManager.requires_skill(target):
            skill_files = surface_groups["official_skill"]
            optional_skill_files = surface_groups["optional_skill"]
            compatibility_skill_files = surface_groups["compatibility_skill"]
            all_skill_files = skill_files or optional_skill_files or compatibility_skill_files
            skill_file = all_skill_files[0] if all_skill_files else None
            skill_path = str(skill_file) if skill_file else ""
            surface_available = bool(skill_files)
            skill_ok = all(path.exists() for path in skill_files) if surface_available else True
            host_report["checks"]["skill"] = {
                "ok": skill_ok,
                "file": skill_path,
                "files": (
                    [str(item) for item in skill_files]
                    if skill_files
                    else ([skill_path] if skill_path else [])
                ),
                "optional_files": [str(item) for item in optional_skill_files],
                "compatibility_files": [str(item) for item in compatibility_skill_files],
                "surface_available": surface_available,
                "mode": (
                    "official-project-and-user-skill-surface"
                    if surface_available
                    else "compatibility-surface-unavailable"
                ),
            }
            if surface_available and not skill_ok:
                host_report["ready"] = False
                host_report["missing"].append("skill")
                host_report["suggestions"].append(
                    f"super-dev skill install super-dev --target {target} --name {skill_name} --force"
                )

        if target == "codex-cli":
            plugin_marketplace = project_dir / ".agents" / "plugins" / "marketplace.json"
            plugin_manifest = (
                project_dir / "plugins" / "super-dev-codex" / ".codex-plugin" / "plugin.json"
            )
            plugin_ok = plugin_marketplace.exists() and plugin_manifest.exists()
            host_report["checks"]["plugin_enhancement"] = {
                "ok": plugin_ok,
                "marketplace_file": str(plugin_marketplace),
                "plugin_manifest": str(plugin_manifest),
                "mode": "repo-marketplace-plugin-enhancement",
                "required": False,
            }
            if not plugin_ok:
                host_report["optional_missing"].append("plugin_enhancement")
        if target == "claude-code":
            plugin_marketplace = project_dir / ".claude-plugin" / "marketplace.json"
            plugin_manifest = (
                project_dir / "plugins" / "super-dev-claude" / ".claude-plugin" / "plugin.json"
            )
            plugin_ok = plugin_marketplace.exists() and plugin_manifest.exists()
            host_report["checks"]["plugin_enhancement"] = {
                "ok": plugin_ok,
                "marketplace_file": str(plugin_marketplace),
                "plugin_manifest": str(plugin_manifest),
                "mode": "repo-marketplace-plugin-enhancement",
                "required": False,
            }
            if not plugin_ok:
                host_report["optional_missing"].append("plugin_enhancement")

        if check_slash:
            required_slash_files = surface_groups["required_slash"]
            optional_slash_files = surface_groups["optional_slash"]
            compatibility_slash_files = surface_groups["compatibility_slash"]
            tracked_slash_files = (
                required_slash_files or optional_slash_files or compatibility_slash_files
            )
            if tracked_slash_files:
                project_slash_file = next(
                    (
                        path
                        for path in tracked_slash_files
                        if str(path).startswith(str(project_dir))
                    ),
                    None,
                )
                global_slash_file = next(
                    (
                        path
                        for path in tracked_slash_files
                        if not str(path).startswith(str(project_dir))
                    ),
                    None,
                )
                project_ok = bool(project_slash_file and project_slash_file.exists())
                global_ok = bool(global_slash_file and global_slash_file.exists())
                slash_ok = (
                    all(path.exists() for path in required_slash_files)
                    if required_slash_files
                    else True
                )
                if required_slash_files:
                    scope = "project" if project_ok else ("global" if global_ok else "missing")
                elif project_ok or global_ok:
                    scope = "optional"
                else:
                    scope = "not-required"
                host_report["checks"]["slash"] = {
                    "ok": slash_ok,
                    "scope": scope,
                    "project_file": str(project_slash_file) if project_slash_file else "",
                    "global_file": str(global_slash_file) if global_slash_file else "",
                    "required_files": [str(item) for item in required_slash_files],
                    "optional_files": [str(item) for item in optional_slash_files],
                    "compatibility_files": [str(item) for item in compatibility_slash_files],
                }
                if required_slash_files and not slash_ok:
                    host_report["ready"] = False
                    host_report["missing"].append("slash")
                    host_report["suggestions"].append(
                        f"super-dev onboard --host {target} --skip-integrate --skip-skill --force --yes"
                    )
            else:
                host_report["checks"]["slash"] = {
                    "ok": True,
                    "scope": "n/a",
                    "project_file": "",
                    "global_file": "",
                    "mode": "rules-only",
                }

        host_report["usage_profile"] = _serialize_host_usage_profile(
            integration_manager=integration_manager,
            target=target,
        )
        usage_profile = host_report["usage_profile"]
        if isinstance(usage_profile, dict):
            precondition_status = str(usage_profile.get("precondition_status", "")).strip()
            precondition_label = str(usage_profile.get("precondition_label", "")).strip()
            precondition_guidance = usage_profile.get("precondition_guidance", [])
            precondition_signals = usage_profile.get("precondition_signals", {})
            precondition_items = usage_profile.get("precondition_items", [])
            host_report["preconditions"] = {
                "status": precondition_status,
                "label": precondition_label,
                "guidance": (
                    precondition_guidance if isinstance(precondition_guidance, list) else []
                ),
                "signals": precondition_signals if isinstance(precondition_signals, dict) else {},
                "items": precondition_items if isinstance(precondition_items, list) else [],
            }
            if precondition_status == "host-auth-required":
                host_report["suggestions"].append(
                    "若宿主报 Invalid API key provided，请先在宿主内完成 /auth 或更新宿主 API key 配置。"
                )
            if precondition_status == "session-restart-required":
                host_report["suggestions"].append("接入后先关闭旧宿主会话，再开一个新会话后重试。")
            if precondition_status == "project-context-required":
                host_report["suggestions"].append(
                    "确认当前聊天/终端绑定的是目标项目，再重新触发 Super Dev。"
                )
        report["hosts"][target] = host_report
        if not host_report["ready"]:
            report["overall_ready"] = False

    return report


def _serialize_host_usage_profile(
    *,
    integration_manager: IntegrationManager,
    target: str,
) -> dict[str, Any]:
    profile = integration_manager.get_adapter_profile(target)
    final_trigger = _display_final_trigger(profile)
    return {
        "host": profile.host,
        "category": profile.category,
        "certification_level": profile.certification_level,
        "certification_label": profile.certification_label,
        "certification_reason": profile.certification_reason,
        "certification_evidence": list(profile.certification_evidence),
        "host_protocol_mode": profile.host_protocol_mode,
        "host_protocol_summary": profile.host_protocol_summary,
        "official_project_surfaces": list(profile.official_project_surfaces),
        "official_user_surfaces": list(profile.official_user_surfaces),
        "optional_project_surfaces": list(profile.optional_project_surfaces),
        "optional_user_surfaces": list(profile.optional_user_surfaces),
        "observed_compatibility_surfaces": list(profile.observed_compatibility_surfaces),
        "usage_mode": profile.usage_mode,
        "primary_entry": profile.primary_entry,
        "trigger_command": profile.trigger_command,
        "final_trigger": final_trigger,
        "entry_variants": list(profile.entry_variants),
        "trigger_context": profile.trigger_context,
        "usage_location": profile.usage_location,
        "requires_restart_after_onboard": profile.requires_restart_after_onboard,
        "restart_required_label": "是" if profile.requires_restart_after_onboard else "否",
        "post_onboard_steps": list(profile.post_onboard_steps),
        "usage_notes": list(profile.usage_notes),
        "smoke_test_prompt": profile.smoke_test_prompt,
        "smoke_test_steps": list(profile.smoke_test_steps),
        "smoke_success_signal": profile.smoke_success_signal,
        "competition_smoke_test_prompt": profile.competition_smoke_test_prompt,
        "competition_smoke_test_steps": list(profile.competition_smoke_test_steps),
        "competition_smoke_success_signal": profile.competition_smoke_success_signal,
        "supports_skill_slash_entry": target == "codex-cli",
        "skill_slash_entry_command": "/super-dev" if target == "codex-cli" else "",
        "skill_slash_entry_note": (
            "Indicates the enabled Skill entry shown in the Codex app slash list, not a project-level custom slash command."
            if target == "codex-cli"
            else ""
        ),
        "flow_contract": build_host_flow_contract(target),
        "flow_probe": build_host_flow_probe(target),
        "path_override": host_path_override_guide(target),
        "precondition_status": profile.precondition_status,
        "precondition_label": profile.precondition_label,
        "precondition_guidance": list(profile.precondition_guidance),
        "precondition_signals": dict(profile.precondition_signals),
        "precondition_items": list(profile.precondition_items),
        "notes": profile.notes,
    }


def _load_host_runtime_validation_state(*, project_dir: Path) -> dict[str, Any]:
    payload = load_host_runtime_validation(project_dir) or {}
    if not isinstance(payload, dict):
        return {"hosts": {}, "updated_at": ""}
    hosts = payload.get("hosts", {})
    if not isinstance(hosts, dict):
        hosts = {}
    return {
        "hosts": hosts,
        "updated_at": str(payload.get("updated_at", "")).strip(),
    }


def _host_runtime_status_label(status: str) -> str:
    mapping = {
        "pending": "待真人验收",
        "passed": "已真人通过",
        "failed": "真人验收失败",
    }
    return mapping.get(status, "待真人验收")


def _build_runtime_evidence_record(
    *,
    host_id: str,
    surface_ready: bool,
    runtime_entry: dict[str, Any],
) -> dict[str, Any]:
    install_mode = get_install_mode(host_id)
    if install_mode == HostInstallMode.MANUAL:
        integration_status = IntegrationStatus.MANUAL
    elif surface_ready:
        integration_status = IntegrationStatus.PROJECT_AND_GLOBAL_INSTALLED
    else:
        integration_status = IntegrationStatus.MISSING
    comment = str(runtime_entry.get("comment", "")).strip()
    evidence = HostRuntimeEvidence(
        host_id=host_id,
        host_display_name=get_display_name(host_id) or host_id,
        summary="integration and runtime evidence are tracked separately",
        integration_status=IntegrationStatusRecord(
            status=integration_status,
            evidence=("surface audit passed",) if surface_ready else ("surface gaps detected",),
            checked_at=str(runtime_entry.get("updated_at", "")).strip(),
            source="surface-audit",
            details="surface ready" if surface_ready else "surface needs repair",
        ),
        runtime_status=RuntimeStatusRecord(
            status=RuntimeStatus(str(runtime_entry.get("status", "")).strip() or "pending"),
            evidence=(comment,) if comment else (),
            checked_at=str(runtime_entry.get("updated_at", "")).strip(),
            source=str(runtime_entry.get("status_source", "")).strip() or "manual",
            details=comment,
        ),
    )
    return serialize_host_runtime_evidence(evidence)


def _update_host_runtime_validation_state(
    *,
    project_dir: Path,
    host: str,
    status: str,
    comment: str,
    actor: str,
) -> tuple[dict[str, Any], Path]:
    payload = _load_host_runtime_validation_state(project_dir=project_dir)
    hosts = dict(payload.get("hosts", {}))
    current = hosts.get(host, {})
    if not isinstance(current, dict):
        current = {}
    timestamp = datetime.now(timezone.utc).isoformat()
    hosts[host] = {
        "status": status,
        "comment": comment.strip(),
        "actor": actor.strip() or "user",
        "updated_at": timestamp,
        "status_source": str(current.get("status_source", "")).strip() or "manual",
    }
    file_path = save_host_runtime_validation(project_dir, {"hosts": hosts})
    updated = _load_host_runtime_validation_state(project_dir=project_dir)
    return updated, file_path


def _build_host_runtime_validation_payload(
    *,
    project_dir: Path,
    targets: list[str],
    detected_meta: dict[str, list[str]],
    report: dict[str, Any],
    usage_profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    runtime_state = _load_host_runtime_validation_state(project_dir=project_dir)
    runtime_hosts = runtime_state.get("hosts", {})
    if not isinstance(runtime_hosts, dict):
        runtime_hosts = {}
    hosts = report.get("hosts", {})
    if not isinstance(hosts, dict):
        hosts = {}
    entries: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    next_actions: list[str] = []
    for target in targets:
        host = hosts.get(target, {}) if isinstance(target, str) else {}
        usage = usage_profiles.get(target, {}) if isinstance(target, str) else {}
        runtime_entry = runtime_hosts.get(target, {}) if isinstance(target, str) else {}
        if not isinstance(host, dict):
            host = {}
        if not isinstance(usage, dict):
            usage = {}
        if not isinstance(runtime_entry, dict):
            runtime_entry = {}
        runtime_status = str(runtime_entry.get("status", "")).strip() or "pending"
        surface_ready = bool(host.get("ready", False))
        precondition_label = usage.get("precondition_label", "-")
        precondition_guidance = usage.get("precondition_guidance", [])
        precondition_items = usage.get("precondition_items", [])
        blocking_reason = ""
        recommended_action = ""
        blocker_type = ""
        if not surface_ready:
            blocking_reason = "宿主接入面仍存在 contract 缺口"
            recommended_action = f"super-dev integrate audit --target {target} --repair --force"
            blocker_type = "surface"
        elif runtime_status == "failed":
            blocking_reason = "宿主真人运行时验收失败"
            recommended_action = f"super-dev integrate audit --target {target} --repair --force"
            blocker_type = "runtime"
        elif runtime_status != "passed":
            blocking_reason = "宿主尚未完成真人运行时验收"
            recommended_action = f'super-dev integrate validate --target {target} --status passed --comment "首轮先进入 research，三文档已真实落盘"'
            blocker_type = "validation"

        if not surface_ready or runtime_status != "passed":
            blockers.append(
                {
                    "host": target,
                    "type": blocker_type or "runtime",
                    "summary": blocking_reason,
                    "next_action": recommended_action,
                }
            )
            if recommended_action and recommended_action not in next_actions:
                next_actions.append(recommended_action)

        if isinstance(precondition_guidance, list):
            for item in precondition_guidance[:2]:
                if (
                    isinstance(item, str)
                    and item.strip()
                    and item not in next_actions
                    and runtime_status != "passed"
                ):
                    next_actions.append(item.strip())

        entries.append(
            {
                "host": target,
                "checks": (
                    host.get("checks", {}) if isinstance(host.get("checks", {}), dict) else {}
                ),
                "missing": (
                    host.get("missing", []) if isinstance(host.get("missing", []), list) else []
                ),
                "suggestions": (
                    host.get("suggestions", [])
                    if isinstance(host.get("suggestions", []), list)
                    else []
                ),
                "surface_ready": surface_ready,
                "integration_status": (
                    "project_and_global_installed" if surface_ready else "repair_needed"
                ),
                "ready_for_delivery": surface_ready and runtime_status == "passed",
                "blocking_reason": blocking_reason,
                "recommended_action": recommended_action,
                "runtime_status": runtime_status,
                "runtime_status_label": _host_runtime_status_label(runtime_status),
                "manual_runtime_status": runtime_status,
                "manual_runtime_status_label": _host_runtime_status_label(runtime_status),
                "manual_runtime_comment": str(runtime_entry.get("comment", "")).strip(),
                "manual_runtime_actor": str(runtime_entry.get("actor", "")).strip(),
                "manual_runtime_updated_at": str(runtime_entry.get("updated_at", "")).strip(),
                "runtime_evidence": _build_runtime_evidence_record(
                    host_id=target,
                    surface_ready=surface_ready,
                    runtime_entry=runtime_entry,
                ),
                "final_trigger": usage.get("final_trigger", "-"),
                "host_protocol_mode": usage.get("host_protocol_mode", "-"),
                "host_protocol_summary": usage.get("host_protocol_summary", "-"),
                "certification_label": usage.get("certification_label", "-"),
                "precondition_label": precondition_label,
                "precondition_guidance": precondition_guidance,
                "precondition_items": (
                    precondition_items if isinstance(precondition_items, list) else []
                ),
                "smoke_test_prompt": usage.get("smoke_test_prompt", ""),
                "smoke_success_signal": usage.get("smoke_success_signal", ""),
                "runtime_checklist": _host_runtime_checklist(
                    target, usage, project_dir=project_dir
                ),
                "pass_criteria": _host_runtime_pass_criteria(target, project_dir=project_dir),
                "flow_probe": build_host_flow_probe(target),
                "resume_probe_prompt": _build_resume_probe_prompt(project_dir, target, usage),
                "resume_checklist": _host_resume_checklist(target, project_dir=project_dir),
                "framework_playbook": load_framework_playbook_summary(project_dir),
            }
        )

    total_hosts = len(entries)
    surface_ready_count = sum(1 for item in entries if bool(item.get("surface_ready", False)))
    runtime_passed_count = sum(
        1 for item in entries if item.get("manual_runtime_status") == "passed"
    )
    runtime_failed_count = sum(
        1 for item in entries if item.get("manual_runtime_status") == "failed"
    )
    runtime_pending_count = sum(
        1 for item in entries if item.get("manual_runtime_status") == "pending"
    )
    fully_ready_count = sum(1 for item in entries if bool(item.get("ready_for_delivery", False)))

    return {
        "project_dir": str(project_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_state_file": str(host_runtime_validation_file(project_dir)),
        "runtime_state_updated_at": runtime_state.get("updated_at", ""),
        "detected_hosts": list(detected_meta.keys()),
        "detection_details": detected_meta,
        "detection_details_pretty": _explain_detection_details(detected_meta),
        "selected_targets": targets,
        "summary": {
            "overall_status": (
                "ready" if total_hosts > 0 and fully_ready_count == total_hosts else "attention"
            ),
            "total_hosts": total_hosts,
            "surface_ready_count": surface_ready_count,
            "runtime_passed_count": runtime_passed_count,
            "runtime_failed_count": runtime_failed_count,
            "runtime_pending_count": runtime_pending_count,
            "fully_ready_count": fully_ready_count,
            "blocking_count": len(blockers),
            "next_actions": next_actions,
        },
        "blockers": blockers,
        "hosts": entries,
    }


def _build_host_compatibility_summary(
    *,
    report: dict[str, Any],
    targets: list[str],
    check_integrate: bool,
    check_skill: bool,
    check_slash: bool,
) -> dict[str, Any]:
    enabled_checks = ["contract"]
    if check_integrate:
        enabled_checks.append("integrate")
    if check_skill and any(IntegrationManager.requires_skill(target) for target in targets):
        enabled_checks.append("skill")
    if check_slash and any(IntegrationManager.supports_slash(target) for target in targets):
        enabled_checks.append("slash")

    per_host: dict[str, dict[str, Any]] = {}
    total_passed = 0
    total_possible = 0
    ready_hosts = 0
    hosts = report.get("hosts", {})
    if not isinstance(hosts, dict):
        hosts = {}

    for target in targets:
        host = hosts.get(target, {})
        checks = host.get("checks", {}) if isinstance(host, dict) else {}
        if not isinstance(checks, dict):
            checks = {}
        passed = 0
        possible = len(enabled_checks)
        for check_name in enabled_checks:
            check_value = checks.get(check_name, {})
            if isinstance(check_value, dict) and bool(check_value.get("ok", False)):
                passed += 1
        score = round((passed / possible) * 100, 2) if possible > 0 else 100.0
        per_host[target] = {
            "score": score,
            "passed": passed,
            "possible": possible,
            "ready": bool(host.get("ready", False)) if isinstance(host, dict) else False,
        }
        total_passed += passed
        total_possible += possible
        if bool(host.get("ready", False)) if isinstance(host, dict) else False:
            ready_hosts += 1

    overall_score = round((total_passed / total_possible) * 100, 2) if total_possible > 0 else 100.0
    return {
        "overall_score": overall_score,
        "ready_hosts": ready_hosts,
        "total_hosts": len(targets),
        "enabled_checks": enabled_checks,
        "hosts": per_host,
    }


def _repair_host_diagnostics(
    *,
    project_dir: Path,
    report: dict[str, Any],
    skill_name: str,
    force: bool,
    check_integrate: bool,
    check_skill: bool,
    check_slash: bool,
) -> dict[str, dict[str, str]]:
    integration_manager = IntegrationManager(project_dir)
    skill_manager = SkillManager(project_dir)
    actions: dict[str, dict[str, str]] = {}

    hosts = report.get("hosts", {})
    if not isinstance(hosts, dict):
        return actions

    for target, host in hosts.items():
        if not isinstance(target, str) or not isinstance(host, dict):
            continue
        missing = host.get("missing", [])
        if not isinstance(missing, list):
            continue

        host_actions: dict[str, str] = {}
        try:
            if check_integrate and "integrate" in missing:
                integration_manager.setup(target=target, force=force)
                host_actions["integrate"] = "fixed"
        except Exception as exc:
            host_actions["integrate"] = f"failed: {exc}"

        try:
            if check_skill and IntegrationManager.requires_skill(target) and "skill" in missing:
                skill_manager.install(
                    source="super-dev",
                    target=target,
                    name=skill_name,
                    force=force,
                )
                host_actions["skill"] = "fixed"
        except Exception as exc:
            host_actions["skill"] = f"failed: {exc}"

        try:
            if check_slash and integration_manager.supports_slash(target):
                integration_manager.setup_slash_command(target=target, force=force)
                integration_manager.setup_global_slash_command(target=target, force=force)
                if "slash" in missing:
                    host_actions["slash"] = "fixed"
        except Exception as exc:
            host_actions["slash"] = f"failed: {exc}"

        if host_actions:
            actions[target] = host_actions

    return actions


def _resolve_deploy_targets(cicd_platform: str, include_runtime: bool) -> list[str]:
    selected = list(_DEPLOY_CICD_FILE_MAP[cicd_platform])
    if include_runtime:
        selected.extend(_DEPLOY_RUNTIME_FILES)
    return selected


def _to_cicd_platform(value: str) -> CICDPlatform:
    if value not in VALID_CICD_PLATFORMS:
        raise ValueError(value)
    return cast(CICDPlatform, value)


def _resolve_deploy_env_hints(cicd_platform: str) -> list[dict[str, str]]:
    if cicd_platform == "all":
        merged: list[dict[str, str]] = []
        seen = set()
        for platform in CICD_PLATFORM_TARGET_IDS:
            for item in _DEPLOY_ENV_HINTS.get(platform, []):
                key = item["name"]
                if key in seen:
                    continue
                seen.add(key)
                merged.append(item)
        return merged
    return list(_DEPLOY_ENV_HINTS.get(cicd_platform, []))


def _resolve_deploy_manual_hints(cicd_platform: str) -> list[str]:
    if cicd_platform == "all":
        merged: list[str] = []
        seen = set()
        for platform in CICD_PLATFORM_TARGET_IDS:
            for item in _DEPLOY_MANUAL_HINTS.get(platform, []):
                if item in seen:
                    continue
                seen.add(item)
                merged.append(item)
        return merged
    return list(_DEPLOY_MANUAL_HINTS.get(cicd_platform, []))


def _collect_workflow_artifact_files(project_dir_path: Path) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    def _append(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen or not resolved.exists() or not resolved.is_file():
            return
        seen.add(resolved)
        files.append(resolved)

    output_dir = project_dir_path / "output"
    if output_dir.exists():
        for pattern in (
            "**/*.md",
            "**/*.json",
            "**/*.html",
            "**/*.css",
            "**/*.js",
            "**/*.yml",
            "**/*.yaml",
            "**/*.png",
        ):
            for file_path in output_dir.glob(pattern):
                _append(file_path)

    for direct in (
        project_dir_path / ".env.deploy.example",
        project_dir_path / ".gitlab-ci.yml",
        project_dir_path / ".azure-pipelines.yml",
        project_dir_path / "Jenkinsfile",
        project_dir_path / "bitbucket-pipelines.yml",
        project_dir_path / "Dockerfile",
        project_dir_path / "docker-compose.yml",
        project_dir_path / ".dockerignore",
    ):
        _append(direct)

    github_dir = project_dir_path / ".github" / "workflows"
    if github_dir.exists():
        for file_path in github_dir.glob("*.yml"):
            _append(file_path)

    k8s_dir = project_dir_path / "k8s"
    if k8s_dir.exists():
        for file_path in k8s_dir.glob("*.yaml"):
            _append(file_path)

    return files


def _resolve_run_project_dir(run_id: str, project_dir: str) -> tuple[dict[str, Any], Path]:
    requested_project_dir = _validate_project_dir(project_dir)
    run = _get_run_state(run_id, requested_project_dir)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")
    run_project_dir = Path(run.get("project_dir") or requested_project_dir).resolve()
    return run, run_project_dir


def _load_ui_review_summary(project_dir_path: Path) -> dict[str, Any] | None:
    output_dir = project_dir_path / "output"
    json_candidates = sorted(output_dir.glob("*-ui-review.json"))
    if json_candidates:
        try:
            payload = json.loads(json_candidates[-1].read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload.setdefault("json_path", str(json_candidates[-1]))
                md_path = json_candidates[-1].with_suffix(".md")
                if md_path.exists():
                    payload.setdefault("report_path", str(md_path))
            return payload
        except Exception as e:
            _api_logger.debug(f"Failed to parse UI review JSON: {e}")
    return None


def _find_ui_review_screenshot(project_dir_path: Path) -> Path | None:
    screenshot_dir = project_dir_path / "output" / "ui-review"
    if not screenshot_dir.exists():
        return None
    candidates = sorted(screenshot_dir.glob("*-preview-desktop.png"))
    return candidates[-1] if candidates else None


def _resolve_deploy_platform_guidance(cicd_platform: str) -> list[str]:
    if cicd_platform == "all":
        merged: list[str] = []
        seen = set()
        for platform in CICD_PLATFORM_TARGET_IDS:
            for item in _DEPLOY_PLATFORM_GUIDANCE.get(platform, []):
                if item in seen:
                    continue
                seen.add(item)
                merged.append(item)
        return merged
    return list(_DEPLOY_PLATFORM_GUIDANCE.get(cicd_platform, []))


def _collect_deploy_env_items(cicd_platform: str, only_missing: bool) -> list[dict[str, Any]]:
    items = []
    for hint in _resolve_deploy_env_hints(cicd_platform):
        name = hint["name"]
        present = bool(os.getenv(name, "").strip())
        if only_missing and present:
            continue
        items.append(
            {
                "name": name,
                "description": hint["description"],
                "present": present,
                "local_export_template": f'export {name}="<value>"',
            }
        )
    return items


def _render_deploy_env_example(
    cicd_platform: str, items: list[dict[str, Any]], only_missing: bool
) -> str:
    lines = [
        "# Super Dev Deployment Environment Template",
        f"# Platform: {cicd_platform}",
        f"# only_missing: {str(only_missing).lower()}",
        "",
    ]
    if not items:
        lines.append("# No variables to export for current filter.")
        return "\n".join(lines) + "\n"

    for item in items:
        lines.append(f"# {item['description']}")
        lines.append(f"{item['name']}=\"<value>\"")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_deploy_checklist_markdown(
    cicd_platform: str,
    only_missing: bool,
    items: list[dict[str, Any]],
    manual_requirements: list[str],
    platform_guidance: list[str],
) -> str:
    lines = [
        "# Deploy Remediation Checklist",
        "",
        f"- Platform: `{cicd_platform}`",
        f"- only_missing: `{str(only_missing).lower()}`",
        f"- Generated at: `{_utc_now()}`",
        "",
        "## Environment Variables",
        "",
        "| Name | Status | Description | Local Template |",
        "|:---|:---:|:---|:---|",
    ]

    if items:
        for item in items:
            status = "present" if item["present"] else "missing"
            lines.append(
                f"| `{item['name']}` | `{status}` | {item['description']} | `{item['local_export_template']}` |"
            )
    else:
        lines.append("| - | - | No variables in current filter | - |")

    lines.extend(["", "## Platform Guidance", ""])
    if platform_guidance:
        for tip in platform_guidance:
            lines.append(f"- {tip}")
    else:
        lines.append("- No guidance available.")

    lines.extend(["", "## Manual Requirements", ""])
    if manual_requirements:
        for requirement in manual_requirements:
            lines.append(f"- {requirement}")
    else:
        lines.append("- No manual requirements.")

    return "\n".join(lines) + "\n"


def _validate_export_file_name(raw_name: str, field_name: str, default_name: str) -> str:
    file_name = (raw_name or default_name).strip()
    if not file_name:
        file_name = default_name
    if "/" in file_name or "\\" in file_name:
        raise ValueError(f"{field_name} 不能包含路径分隔符")
    return file_name


def _generate_deploy_remediation_files(
    project_dir_path: Path,
    cicd_platform: str,
    only_missing: bool,
    split_by_platform: bool,
    env_file_name: str,
    checklist_file_name: str,
) -> dict[str, Any]:
    output_dir = project_dir_path / "output" / "deploy"
    output_dir.mkdir(parents=True, exist_ok=True)

    remediation_items = _collect_deploy_env_items(
        cicd_platform=cicd_platform,
        only_missing=only_missing,
    )
    manual_requirements = _resolve_deploy_manual_hints(cicd_platform)
    platform_guidance = _resolve_deploy_platform_guidance(cicd_platform)

    env_content = _render_deploy_env_example(
        cicd_platform=cicd_platform,
        items=remediation_items,
        only_missing=only_missing,
    )
    checklist_content = _render_deploy_checklist_markdown(
        cicd_platform=cicd_platform,
        only_missing=only_missing,
        items=remediation_items,
        manual_requirements=manual_requirements,
        platform_guidance=platform_guidance,
    )

    env_path = project_dir_path / env_file_name
    checklist_path = output_dir / checklist_file_name
    env_path.write_text(env_content, encoding="utf-8")
    checklist_path.write_text(checklist_content, encoding="utf-8")

    generated_files = [str(env_path), str(checklist_path)]
    per_platform_files: list[dict[str, Any]] = []
    should_split = cicd_platform == "all" and split_by_platform
    if should_split:
        platform_dir = output_dir / "platforms"
        platform_dir.mkdir(parents=True, exist_ok=True)
        for platform in CICD_PLATFORM_TARGET_IDS:
            platform_items = _collect_deploy_env_items(
                cicd_platform=platform,
                only_missing=only_missing,
            )
            platform_env = platform_dir / f".env.deploy.{platform}.example"
            platform_checklist = platform_dir / f"{platform}-secrets-checklist.md"

            platform_env.write_text(
                _render_deploy_env_example(
                    cicd_platform=platform,
                    items=platform_items,
                    only_missing=only_missing,
                ),
                encoding="utf-8",
            )
            platform_checklist.write_text(
                _render_deploy_checklist_markdown(
                    cicd_platform=platform,
                    only_missing=only_missing,
                    items=platform_items,
                    manual_requirements=_resolve_deploy_manual_hints(platform),
                    platform_guidance=_resolve_deploy_platform_guidance(platform),
                ),
                encoding="utf-8",
            )

            generated_files.extend([str(platform_env), str(platform_checklist)])
            per_platform_files.append(
                {
                    "platform": platform,
                    "items_count": len(platform_items),
                    "env_file": {
                        "file_name": platform_env.name,
                        "path": str(platform_env),
                    },
                    "checklist_file": {
                        "file_name": platform_checklist.name,
                        "path": str(platform_checklist),
                    },
                }
            )

    return {
        "remediation_items": remediation_items,
        "manual_requirements": manual_requirements,
        "platform_guidance": platform_guidance,
        "env_path": env_path,
        "checklist_path": checklist_path,
        "per_platform_files": per_platform_files,
        "generated_files": generated_files,
    }


def _normalize_string_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _build_policy_response(
    policy: PipelinePolicy, manager: PipelinePolicyManager
) -> dict[str, Any]:
    return {
        "require_redteam": policy.require_redteam,
        "require_quality_gate": policy.require_quality_gate,
        "require_rehearsal_verify": policy.require_rehearsal_verify,
        "min_quality_threshold": policy.min_quality_threshold,
        "allowed_cicd_platforms": policy.allowed_cicd_platforms,
        "require_host_profile": policy.require_host_profile,
        "required_hosts": policy.required_hosts,
        "enforce_required_hosts_ready": policy.enforce_required_hosts_ready,
        "min_required_host_score": policy.min_required_host_score,
        "policy_file": str(manager.policy_path),
        "policy_exists": manager.policy_path.exists(),
    }


# ==================== API 路由 ====================
# NOTE: Routes below use /api/ prefix for backward compatibility.
# The canonical prefix is /api/v1/ — see v1_router above.


@app.get("/api/health")
@v1_router.get("/health")
@app.get("/health")  # Alias for k8s probes and load balancers
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": __version__}


@app.get("/api/config")
@v1_router.get("/config")
async def get_config(project_dir: str = ".") -> dict:
    """获取项目配置"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if not manager.exists():
            raise HTTPException(status_code=404, detail="项目未初始化")

        config = manager.config
        return {
            "name": config.name,
            "description": config.description,
            "version": config.version,
            "platform": config.platform,
            "frontend": config.frontend,
            "backend": config.backend,
            "database": config.database,
            "domain": config.domain,
            "language_preferences": config.language_preferences,
            "quality_gate": config.quality_gate,
            "host_compatibility_min_score": config.host_compatibility_min_score,
            "host_compatibility_min_ready_hosts": config.host_compatibility_min_ready_hosts,
            "host_profile_targets": config.host_profile_targets,
            "host_profile_enforce_selected": config.host_profile_enforce_selected,
            "phases": config.phases,
            "experts": config.experts,
            "output_dir": config.output_dir,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policy", response_model=PipelinePolicyResponse)
async def get_policy(project_dir: str = ".") -> dict[str, Any]:
    """获取 pipeline policy"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = PipelinePolicyManager(project_dir_path)
        policy = manager.load()
        return _build_policy_response(policy=policy, manager=manager)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policy/presets")
async def list_policy_presets() -> dict[str, Any]:
    """列出可用策略预设"""
    return {
        "presets": [
            {
                "id": "default",
                "description": "默认策略（兼顾灵活性）",
            },
            {
                "id": "balanced",
                "description": "团队协作增强（要求 host profile）",
            },
            {
                "id": "enterprise",
                "description": "商业级强治理（更高质量阈值 + host profile，可按项目配置关键宿主）",
            },
        ]
    }


@app.put("/api/policy", response_model=PipelinePolicyResponse, dependencies=[Depends(get_api_key)])
async def update_policy(
    request: PipelinePolicyUpdateRequest,
    project_dir: str = ".",
) -> dict[str, Any]:
    """更新 pipeline policy"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = PipelinePolicyManager(project_dir_path)
        preset_name = request.preset.strip().lower() if isinstance(request.preset, str) else ""
        if preset_name:
            current = manager.build_preset(preset_name)
        else:
            current = manager.load()

        min_quality_threshold = current.min_quality_threshold
        if request.min_quality_threshold is not None:
            if request.min_quality_threshold < 0 or request.min_quality_threshold > 100:
                raise HTTPException(
                    status_code=400, detail="min_quality_threshold 必须在 0-100 之间"
                )
            min_quality_threshold = request.min_quality_threshold

        allowed_cicd_platforms = current.allowed_cicd_platforms
        if request.allowed_cicd_platforms is not None:
            normalized = _normalize_string_list(request.allowed_cicd_platforms)
            if not normalized:
                raise HTTPException(status_code=400, detail="allowed_cicd_platforms 不能为空")
            invalid = [item for item in normalized if item not in VALID_CICD_PLATFORMS]
            if invalid:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效 CI/CD 平台: {', '.join(invalid)}",
                )
            allowed_cicd_platforms = normalized

        required_hosts = current.required_hosts
        if request.required_hosts is not None:
            normalized_hosts = _normalize_string_list(request.required_hosts)
            allowed_hosts = {item["id"] for item in HOST_TOOL_CATALOG}
            invalid_hosts = [item for item in normalized_hosts if item not in allowed_hosts]
            if invalid_hosts:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效宿主: {', '.join(invalid_hosts)}",
                )
            required_hosts = normalized_hosts

        min_required_host_score = current.min_required_host_score
        if request.min_required_host_score is not None:
            if request.min_required_host_score < 0 or request.min_required_host_score > 100:
                raise HTTPException(
                    status_code=400, detail="min_required_host_score 必须在 0-100 之间"
                )
            min_required_host_score = request.min_required_host_score

        updated = PipelinePolicy(
            require_redteam=(
                request.require_redteam
                if request.require_redteam is not None
                else current.require_redteam
            ),
            require_quality_gate=(
                request.require_quality_gate
                if request.require_quality_gate is not None
                else current.require_quality_gate
            ),
            require_rehearsal_verify=(
                request.require_rehearsal_verify
                if request.require_rehearsal_verify is not None
                else current.require_rehearsal_verify
            ),
            min_quality_threshold=min_quality_threshold,
            allowed_cicd_platforms=allowed_cicd_platforms,
            require_host_profile=(
                request.require_host_profile
                if request.require_host_profile is not None
                else current.require_host_profile
            ),
            required_hosts=required_hosts,
            enforce_required_hosts_ready=(
                request.enforce_required_hosts_ready
                if request.enforce_required_hosts_ready is not None
                else current.enforce_required_hosts_ready
            ),
            min_required_host_score=min_required_host_score,
        )
        manager.save(updated)
        return _build_policy_response(policy=updated, manager=manager)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/init", dependencies=[Depends(get_api_key)])
@v1_router.post("/init", dependencies=[Depends(get_api_key)])
async def init_project(request: ProjectInitRequest, project_dir: str = ".") -> dict:
    """初始化项目"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if manager.exists():
            raise HTTPException(status_code=400, detail="项目已初始化")

        config = manager.create(
            name=request.name,
            description=request.description,
            platform=request.platform,
            frontend=request.frontend,
            backend=request.backend,
            domain=request.domain,
            language_preferences=request.language_preferences,
            quality_gate=request.quality_gate,
            host_compatibility_min_score=request.host_compatibility_min_score,
            host_compatibility_min_ready_hosts=request.host_compatibility_min_ready_hosts,
            host_profile_targets=request.host_profile_targets,
            host_profile_enforce_selected=request.host_profile_enforce_selected,
        )

        return {
            "status": "success",
            "message": "项目已初始化",
            "config": {
                "name": config.name,
                "platform": config.platform,
                "frontend": config.frontend,
                "backend": config.backend,
            },
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config", dependencies=[Depends(get_api_key)])
async def update_config(updates: dict, project_dir: str = ".") -> dict:
    """更新项目配置"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if not manager.exists():
            raise HTTPException(status_code=404, detail="项目未初始化")

        config = manager.update(**updates)
        return {"status": "success", "config": config.__dict__}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workflow/run", dependencies=[Depends(get_api_key)])
@v1_router.post("/workflow/run", dependencies=[Depends(get_api_key)])
async def run_workflow(
    request: WorkflowRunRequest, background_tasks: BackgroundTasks, project_dir: str = "."
) -> WorkflowRunResponse:
    """运行工作流"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if not manager.exists():
            raise HTTPException(status_code=404, detail="项目未初始化")

        # 更新门禁配置
        workflow_updates: dict[str, Any] = {}
        if request.quality_gate is not None:
            workflow_updates["quality_gate"] = request.quality_gate
        if request.host_compatibility_min_score is not None:
            workflow_updates["host_compatibility_min_score"] = request.host_compatibility_min_score
        if request.host_compatibility_min_ready_hosts is not None:
            workflow_updates["host_compatibility_min_ready_hosts"] = (
                request.host_compatibility_min_ready_hosts
            )
        if request.host_profile_targets is not None:
            workflow_updates["host_profile_targets"] = request.host_profile_targets
        if request.host_profile_enforce_selected is not None:
            workflow_updates["host_profile_enforce_selected"] = (
                request.host_profile_enforce_selected
            )
        if request.language_preferences is not None:
            workflow_updates["language_preferences"] = request.language_preferences
        if workflow_updates:
            manager.update(**workflow_updates)
        config = manager.config

        # 解析阶段
        phases = None
        requested_phase_names = None
        if request.phases:
            phase_map = {
                "discovery": Phase.DISCOVERY,
                "intelligence": Phase.INTELLIGENCE,
                "drafting": Phase.DRAFTING,
                "redteam": Phase.REDTEAM,
                "qa": Phase.QA,
                "delivery": Phase.DELIVERY,
                "deployment": Phase.DEPLOYMENT,
            }
            invalid_phases = [p for p in request.phases if p not in phase_map]
            if invalid_phases:
                raise HTTPException(
                    status_code=400, detail=f"无效阶段: {', '.join(invalid_phases)}"
                )
            phases = [phase_map[p] for p in request.phases]
            requested_phase_names = list(request.phases)
        else:
            requested_phase_names = list(manager.config.phases)

        # 生成运行 ID
        import uuid

        run_id = str(uuid.uuid4())[:8]

        _store_run_state(
            run_id,
            persist_dir=project_dir_path,
            status="queued",
            project_dir=str(project_dir_path),
            requested_phases=requested_phase_names,
            completed_phases=[],
            progress=0,
            message="工作流排队中",
            cancel_requested=False,
            error=None,
            started_at=_utc_now(),
            finished_at=None,
            results=[],
        )

        # 后台运行工作流
        async def _run_workflow_background() -> None:
            if _is_cancel_requested(run_id):
                _store_run_state(
                    run_id,
                    persist_dir=project_dir_path,
                    status="cancelled",
                    message="工作流已取消（启动前）",
                    finished_at=_utc_now(),
                )
                return

            _store_run_state(
                run_id,
                persist_dir=project_dir_path,
                status="running",
                message="工作流运行中",
                progress=5,
            )
            try:
                engine = WorkflowEngine(project_dir_path)
                context = WorkflowContext(
                    project_dir=project_dir_path,
                    config=manager,
                    user_input={
                        "name": request.name or config.name or project_dir_path.name,
                        "description": (
                            request.description
                            if request.description is not None
                            else config.description
                        ),
                        "platform": request.platform or config.platform,
                        "frontend": request.frontend or config.frontend,
                        "backend": request.backend or config.backend,
                        "domain": request.domain if request.domain is not None else config.domain,
                        "language_preferences": (
                            request.language_preferences
                            if request.language_preferences is not None
                            else config.language_preferences
                        ),
                        "cicd": request.cicd or "github",
                        "orm": request.orm,
                        "offline": request.offline,
                        "quality_threshold": request.quality_gate,
                        "host_compatibility_min_score": (
                            request.host_compatibility_min_score
                            if request.host_compatibility_min_score is not None
                            else config.host_compatibility_min_score
                        ),
                        "host_compatibility_min_ready_hosts": (
                            request.host_compatibility_min_ready_hosts
                            if request.host_compatibility_min_ready_hosts is not None
                            else config.host_compatibility_min_ready_hosts
                        ),
                        "host_profile_targets": (
                            request.host_profile_targets
                            if request.host_profile_targets is not None
                            else config.host_profile_targets
                        ),
                        "host_profile_enforce_selected": (
                            request.host_profile_enforce_selected
                            if request.host_profile_enforce_selected is not None
                            else config.host_profile_enforce_selected
                        ),
                    },
                )
                results = await engine.run(
                    phases=phases,
                    context=context,
                    stop_requested=lambda: _is_cancel_requested(run_id),
                )

                planned = max(len(requested_phase_names or []), 1)
                completed = []
                serialized_results = []
                for phase, result in results.items():
                    completed.append(phase.value)
                    serialized_results.append(
                        {
                            "phase": phase.value,
                            "success": result.success,
                            "duration": result.duration,
                            "quality_score": result.quality_score,
                            "errors": list(result.errors or []),
                            "output": _sanitize_run_payload(result.output),
                        }
                    )

                all_success = (
                    all(item["success"] for item in serialized_results)
                    if serialized_results
                    else True
                )
                progress = min(100, int(len(completed) / planned * 100))
                if _is_cancel_requested(run_id):
                    status = "cancelled"
                    message = "工作流已取消"
                else:
                    status = "completed" if all_success and progress >= 100 else "failed"
                    message = "工作流执行完成" if status == "completed" else "工作流执行失败"

                _store_run_state(
                    run_id,
                    persist_dir=project_dir_path,
                    status=status,
                    message=message,
                    completed_phases=completed,
                    progress=progress,
                    results=serialized_results,
                    finished_at=_utc_now(),
                )
            except Exception as e:
                cancel_requested = _is_cancel_requested(run_id)
                status = "cancelled" if cancel_requested else "failed"
                message = "工作流已取消" if cancel_requested else "工作流执行异常"
                _store_run_state(
                    run_id,
                    persist_dir=project_dir_path,
                    status=status,
                    message=message,
                    cancel_requested=cancel_requested,
                    error=str(e),
                    finished_at=_utc_now(),
                )

        def _run_workflow_background_sync() -> None:
            asyncio.run(_run_workflow_background())

        background_tasks.add_task(_run_workflow_background_sync)

        return WorkflowRunResponse(
            status="started", message=f"工作流已启动 (ID: {run_id})", run_id=run_id
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/status/{run_id}")
@v1_router.get("/workflow/status/{run_id}")
async def get_workflow_status(run_id: str, project_dir: str = ".") -> dict:
    """获取工作流状态"""
    run_id = _validate_run_id(run_id)
    project_dir_path = _validate_project_dir(project_dir)
    run = _get_run_state(run_id, project_dir_path)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")
    enriched = _with_pipeline_summary(run, project_dir_path)
    _store_run_state(
        run_id, persist_dir=project_dir_path, pipeline_summary=enriched["pipeline_summary"]
    )
    return enriched


@app.get("/api/workflow/docs-confirmation")
@v1_router.get("/workflow/docs-confirmation")
async def get_workflow_docs_confirmation(project_dir: str = ".") -> dict:
    """获取三文档确认状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = load_docs_confirmation(project_dir_path) or {}
    return {
        "project_dir": str(project_dir_path),
        "status": str(payload.get("status", "")).strip() or "pending_review",
        "comment": str(payload.get("comment", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "exists": bool(payload),
        "file_path": str(docs_confirmation_file(project_dir_path)),
    }


@app.post("/api/workflow/docs-confirmation", dependencies=[Depends(get_api_key)])
@v1_router.post("/workflow/docs-confirmation", dependencies=[Depends(get_api_key)])
async def update_workflow_docs_confirmation(
    request: WorkflowDocsConfirmationRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新三文档确认状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = {
        "status": request.status,
        "comment": request.comment.strip(),
        "actor": request.actor.strip() or "user",
        "run_id": run_id.strip(),
    }
    file_path = save_docs_confirmation(project_dir_path, payload)
    return {
        "status": request.status,
        "comment": payload["comment"],
        "actor": payload["actor"],
        "run_id": payload["run_id"],
        "updated_at": (load_docs_confirmation(project_dir_path) or {}).get("updated_at", ""),
        "file_path": str(file_path),
    }


@app.get("/api/workflow/preview-confirmation")
@v1_router.get("/workflow/preview-confirmation")
async def get_workflow_preview_confirmation(project_dir: str = ".") -> dict:
    """获取前端预览确认状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = load_preview_confirmation(project_dir_path) or {}
    return {
        "project_dir": str(project_dir_path),
        "status": str(payload.get("status", "")).strip() or "pending_review",
        "comment": str(payload.get("comment", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "exists": bool(payload),
        "file_path": str(preview_confirmation_file(project_dir_path)),
    }


@app.post("/api/workflow/preview-confirmation", dependencies=[Depends(get_api_key)])
@v1_router.post("/workflow/preview-confirmation", dependencies=[Depends(get_api_key)])
async def update_workflow_preview_confirmation(
    request: WorkflowPreviewConfirmationRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新前端预览确认状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = {
        "status": request.status,
        "comment": request.comment.strip(),
        "actor": request.actor.strip() or "user",
        "run_id": run_id.strip(),
    }
    file_path = save_preview_confirmation(project_dir_path, payload)
    return {
        "status": request.status,
        "comment": payload["comment"],
        "actor": payload["actor"],
        "run_id": payload["run_id"],
        "updated_at": (load_preview_confirmation(project_dir_path) or {}).get("updated_at", ""),
        "file_path": str(file_path),
    }


@app.get("/api/workflow/ui-revision")
async def get_workflow_ui_revision(project_dir: str = ".") -> dict:
    """获取 UI 改版状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = load_ui_revision(project_dir_path) or {}
    return {
        "project_dir": str(project_dir_path),
        "status": str(payload.get("status", "")).strip() or "pending_review",
        "comment": str(payload.get("comment", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "exists": bool(payload),
        "file_path": str(ui_revision_file(project_dir_path)),
    }


@app.post("/api/workflow/ui-revision", dependencies=[Depends(get_api_key)])
async def update_workflow_ui_revision(
    request: WorkflowUIRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新 UI 改版状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = {
        "status": request.status,
        "comment": request.comment.strip(),
        "actor": request.actor.strip() or "user",
        "run_id": run_id.strip(),
    }
    file_path = save_ui_revision(project_dir_path, payload)
    return {
        "status": request.status,
        "comment": payload["comment"],
        "actor": payload["actor"],
        "run_id": payload["run_id"],
        "updated_at": (load_ui_revision(project_dir_path) or {}).get("updated_at", ""),
        "file_path": str(file_path),
    }


@app.get("/api/workflow/architecture-revision")
async def get_workflow_architecture_revision(project_dir: str = ".") -> dict:
    """获取架构返工状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = load_architecture_revision(project_dir_path) or {}
    return {
        "project_dir": str(project_dir_path),
        "status": str(payload.get("status", "")).strip() or "pending_review",
        "comment": str(payload.get("comment", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "exists": bool(payload),
        "file_path": str(architecture_revision_file(project_dir_path)),
    }


@app.post("/api/workflow/architecture-revision", dependencies=[Depends(get_api_key)])
async def update_workflow_architecture_revision(
    request: WorkflowArchitectureRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新架构返工状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = {
        "status": request.status,
        "comment": request.comment.strip(),
        "actor": request.actor.strip() or "user",
        "run_id": run_id.strip(),
    }
    file_path = save_architecture_revision(project_dir_path, payload)
    return {
        "status": request.status,
        "comment": payload["comment"],
        "actor": payload["actor"],
        "run_id": payload["run_id"],
        "updated_at": (load_architecture_revision(project_dir_path) or {}).get("updated_at", ""),
        "file_path": str(file_path),
    }


@app.get("/api/workflow/quality-revision")
async def get_workflow_quality_revision(project_dir: str = ".") -> dict:
    """获取质量返工状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = load_quality_revision(project_dir_path) or {}
    return {
        "project_dir": str(project_dir_path),
        "status": str(payload.get("status", "")).strip() or "pending_review",
        "comment": str(payload.get("comment", "")).strip(),
        "actor": str(payload.get("actor", "")).strip(),
        "run_id": str(payload.get("run_id", "")).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "exists": bool(payload),
        "file_path": str(quality_revision_file(project_dir_path)),
    }


@app.post("/api/workflow/quality-revision", dependencies=[Depends(get_api_key)])
async def update_workflow_quality_revision(
    request: WorkflowQualityRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新质量返工状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    payload = {
        "status": request.status,
        "comment": request.comment.strip(),
        "actor": request.actor.strip() or "user",
        "run_id": run_id.strip(),
    }
    file_path = save_quality_revision(project_dir_path, payload)
    return {
        "status": request.status,
        "comment": payload["comment"],
        "actor": payload["actor"],
        "run_id": payload["run_id"],
        "updated_at": (load_quality_revision(project_dir_path) or {}).get("updated_at", ""),
        "file_path": str(file_path),
    }


@app.post("/api/workflow/cancel/{run_id}", dependencies=[Depends(get_api_key)])
async def cancel_workflow(run_id: str, project_dir: str = ".") -> dict:
    """取消工作流运行"""
    run_id = _validate_run_id(run_id)
    project_dir_path = _validate_project_dir(project_dir)
    run = _get_run_state(run_id, project_dir_path)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")

    status = str(run.get("status", "unknown"))
    if status in {"completed", "failed", "cancelled"}:
        return {
            "run_id": run_id,
            "status": status,
            "message": "运行已结束，无需取消",
        }

    if status == "queued":
        _store_run_state(
            run_id,
            persist_dir=project_dir_path,
            status="cancelled",
            cancel_requested=True,
            message="工作流已取消（未开始执行）",
            finished_at=_utc_now(),
        )
        return {
            "run_id": run_id,
            "status": "cancelled",
            "message": "工作流已取消",
        }

    _store_run_state(
        run_id,
        persist_dir=project_dir_path,
        status="cancelling",
        cancel_requested=True,
        message="已收到取消请求，将在当前阶段完成后停止",
    )
    return {
        "run_id": run_id,
        "status": "cancelling",
        "message": "取消请求已受理",
    }


@app.get("/api/workflow/runs")
async def list_workflow_runs(project_dir: str = ".", limit: int = 20) -> dict:
    """列出工作流运行历史（最近优先）"""
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit 必须大于 0")
    if limit > 500:
        limit = 500

    project_dir_path = _validate_project_dir(project_dir)
    runs = [
        _with_pipeline_summary(run, project_dir_path)
        for run in _list_persisted_runs(project_dir_path, limit=limit)
    ]
    return {"runs": runs, "count": len(runs)}


@app.get("/api/workflow/artifacts/{run_id}")
async def list_workflow_artifacts(run_id: str, project_dir: str = ".") -> dict:
    """列出某次工作流可下载的交付物文件。"""
    run, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    artifact_files = _collect_workflow_artifact_files(run_project_dir)
    items = []
    for file_path in artifact_files:
        try:
            relative = str(file_path.relative_to(run_project_dir))
        except ValueError:
            relative = file_path.name
        items.append(
            {
                "name": file_path.name,
                "path": str(file_path),
                "relative_path": str(relative),
                "size_bytes": file_path.stat().st_size,
            }
        )

    return {
        "run_id": run_id,
        "project_dir": str(run_project_dir),
        "count": len(items),
        "items": items,
    }


@app.get("/api/workflow/artifacts/{run_id}/archive")
async def download_workflow_artifacts_archive(run_id: str, project_dir: str = ".") -> FileResponse:
    """下载某次工作流交付物压缩包。"""
    _, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    artifact_files = _collect_workflow_artifact_files(run_project_dir)
    if not artifact_files:
        raise HTTPException(status_code=404, detail="未找到可下载的交付物文件")

    archive_dir = run_project_dir / "output" / "artifacts"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"workflow-{run_id}-artifacts.zip"

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in artifact_files:
            try:
                arcname = str(file_path.relative_to(run_project_dir))
            except ValueError:
                arcname = file_path.name
            zf.write(file_path, arcname=arcname)

    return FileResponse(
        path=archive_path,
        media_type="application/zip",
        filename=archive_path.name,
    )


@app.get("/api/workflow/ui-review/{run_id}")
async def get_workflow_ui_review(run_id: str, project_dir: str = ".") -> dict:
    """获取某次工作流的 UI 审查摘要。"""
    run, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    summary = _load_ui_review_summary(run_project_dir)
    screenshot = _find_ui_review_screenshot(run_project_dir)

    qa_result = None
    if isinstance(run.get("results"), list):
        qa_result = next((item for item in run["results"] if item.get("phase") == "qa"), None)

    if summary is None and qa_result and isinstance(qa_result.get("output"), dict):
        nested = qa_result["output"].get("ui_review")
        if isinstance(nested, dict):
            summary = nested

    if summary is None and screenshot is None:
        raise HTTPException(status_code=404, detail="未找到 UI 审查结果")

    screenshot_url = ""
    screenshot_relative_path = ""
    if screenshot is not None:
        screenshot_url = (
            f"/api/workflow/ui-review/{run_id}/screenshot?"
            f"{urlencode({'project_dir': str(run_project_dir)})}"
        )
        try:
            screenshot_relative_path = str(screenshot.relative_to(run_project_dir))
        except ValueError:
            screenshot_relative_path = screenshot.name

    return {
        "run_id": run_id,
        "project_dir": str(run_project_dir),
        "summary": summary or {},
        "report_path": summary.get("report_path", "") if isinstance(summary, dict) else "",
        "json_path": summary.get("json_path", "") if isinstance(summary, dict) else "",
        "screenshot": {
            "exists": screenshot is not None,
            "path": str(screenshot) if screenshot is not None else "",
            "relative_path": screenshot_relative_path,
            "url": screenshot_url,
        },
    }


@app.get("/api/workflow/ui-review/{run_id}/screenshot")
async def download_workflow_ui_review_screenshot(
    run_id: str, project_dir: str = "."
) -> FileResponse:
    """获取某次工作流 UI 审查截图。"""
    _, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    screenshot = _find_ui_review_screenshot(run_project_dir)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="未找到 UI 审查截图")
    return FileResponse(path=screenshot, media_type="image/png", filename=screenshot.name)


@app.get("/api/experts")
@v1_router.get("/experts")
async def list_experts() -> dict:
    """列出可用专家"""
    return {"experts": list_expert_catalog()}


@app.post("/api/experts/{expert_id}/advice", dependencies=[Depends(get_api_key)])
async def generate_expert_advice(
    expert_id: str,
    request: ExpertAdviceRequest,
    project_dir: str = ".",
) -> dict:
    """生成专家建议并写入 output 目录。"""
    expert_id = expert_id.upper()
    if not has_expert(expert_id):
        raise HTTPException(status_code=404, detail=f"未知专家: {expert_id}")

    project_dir_path = _validate_project_dir(project_dir)
    file_path, content = save_expert_advice(
        project_dir=project_dir_path,
        expert_id=expert_id,
        prompt=request.prompt,
    )
    return {
        "expert_id": expert_id,
        "project_dir": str(project_dir_path),
        "file_path": str(file_path),
        "file_name": file_path.name,
        "content": content,
    }


@app.get("/api/experts/advice/history")
async def get_expert_advice_history(project_dir: str = ".", limit: int = 20) -> dict:
    """列出已生成的专家建议历史。"""
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit 必须大于 0")
    if limit > 500:
        limit = 500

    project_dir_path = _validate_project_dir(project_dir)
    items = list_expert_advice_history(project_dir_path, limit=limit)
    return {"items": items, "count": len(items)}


@app.get("/api/experts/advice/content")
async def get_expert_advice_content(file_name: str, project_dir: str = ".") -> dict:
    """读取某个专家建议内容。"""
    project_dir_path = _validate_project_dir(project_dir)
    try:
        file_path, content = read_expert_advice(project_dir_path, file_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"建议文件不存在: {file_name}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "content": content,
    }


@app.get("/api/phases")
@v1_router.get("/phases")
async def list_phases() -> dict:
    """列出工作流阶段"""
    phases = [
        {"id": "discovery", "name": "需求发现", "description": "收集和分析用户需求"},
        {"id": "intelligence", "name": "情报收集", "description": "市场研究、竞品分析"},
        {"id": "drafting", "name": "专家起草", "description": "专家协作生成文档"},
        {"id": "redteam", "name": "红队审查", "description": "安全、性能审查"},
        {"id": "qa", "name": "质量门禁", "description": "质量检查和验证"},
        {"id": "delivery", "name": "幻影交付", "description": "生成原型预览"},
        {"id": "deployment", "name": "工业化部署", "description": "生成部署配置"},
    ]
    return {"phases": phases}


@app.get("/api/catalogs")
async def get_catalogs() -> dict:
    """返回前端初始化和工作流表单所需的选项目录。"""
    return {
        "platforms": PLATFORM_CATALOG,
        "frontends": PIPELINE_FRONTEND_TEMPLATE_CATALOG,
        "backends": SUPPORTED_BACKEND_TEMPLATES,
        "domains": DOMAIN_CATALOG,
        "cicd_platforms": CICD_PLATFORM_CATALOG,
        "host_tools": _build_host_tool_catalog_payload(),
        "languages": SUPPORTED_LANGUAGE_PREFERENCES,
    }


@app.get("/api/hosts/doctor")
async def doctor_hosts(
    project_dir: str = ".",
    host: str | None = None,
    auto: bool = False,
    skill_name: str = "super-dev",
    skip_integrate: bool = False,
    skip_skill: bool = False,
    skip_slash: bool = False,
    repair: bool = False,
    force: bool = False,
) -> dict:
    """诊断宿主接入状态，并返回兼容性评分。"""
    project_dir_path = _validate_project_dir(project_dir)
    integration_manager = IntegrationManager(project_dir_path)
    all_targets = [item.name for item in integration_manager.list_targets()]
    available_targets = _public_host_targets(integration_manager=integration_manager)
    detected_targets, detected_meta = _detect_host_targets(available_targets)

    if host:
        if host not in all_targets:
            raise HTTPException(status_code=400, detail=f"不支持的 host: {host}")
        targets = [host]
    elif auto:
        targets = detected_targets or available_targets
    else:
        targets = available_targets

    check_integrate = not skip_integrate
    check_skill = not skip_skill
    check_slash = not skip_slash

    report = _collect_host_diagnostics(
        project_dir=project_dir_path,
        targets=targets,
        skill_name=skill_name,
        check_integrate=check_integrate,
        check_skill=check_skill,
        check_slash=check_slash,
    )
    compatibility = _build_host_compatibility_summary(
        report=report,
        targets=targets,
        check_integrate=check_integrate,
        check_skill=check_skill,
        check_slash=check_slash,
    )
    repair_actions: dict[str, dict[str, str]] = {}
    if repair:
        repair_actions = _repair_host_diagnostics(
            project_dir=project_dir_path,
            report=report,
            skill_name=skill_name,
            force=force,
            check_integrate=check_integrate,
            check_skill=check_skill,
            check_slash=check_slash,
        )
        report = _collect_host_diagnostics(
            project_dir=project_dir_path,
            targets=targets,
            skill_name=skill_name,
            check_integrate=check_integrate,
            check_skill=check_skill,
            check_slash=check_slash,
        )
        compatibility = _build_host_compatibility_summary(
            report=report,
            targets=targets,
            check_integrate=check_integrate,
            check_skill=check_skill,
            check_slash=check_slash,
        )

    report["compatibility"] = compatibility
    if repair:
        report["repair_actions"] = repair_actions

    usage_profiles = {
        target: _serialize_host_usage_profile(
            integration_manager=integration_manager,
            target=target,
        )
        for target in targets
    }
    decision_card = _build_detected_host_decision_card(
        project_dir=project_dir_path,
        integration_manager=integration_manager,
        detected_targets=detected_targets,
        detected_meta=detected_meta,
        preferred_targets=targets if host else None,
    )

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "selected_targets": targets,
        "detected_targets": detected_targets,
        "detection_details": detected_meta,
        "detection_details_pretty": _explain_detection_details(detected_meta),
        "report": report,
        "compatibility": compatibility,
        "usage_profiles": usage_profiles,
        "decision_card": decision_card,
        "primary_repair_action": _build_primary_repair_action(
            report=report,
            targets=targets,
            integration_manager=integration_manager,
            decision_card=decision_card,
        ),
        "session_resume_cards": {
            target: _build_session_resume_card(
                project_dir_path,
                target,
                usage_profiles[target],
            )
            for target in targets
        },
        "auto": auto,
        "repair": repair,
    }


@app.get("/api/hosts/validate")
async def validate_hosts(
    project_dir: str = ".",
    host: str | None = None,
    auto: bool = False,
    skill_name: str = "super-dev",
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    integration_manager = IntegrationManager(project_dir_path)
    all_targets = [item.name for item in integration_manager.list_targets()]
    available_targets = _public_host_targets(integration_manager=integration_manager)
    detected_targets, detected_meta = _detect_host_targets(available_targets)

    if host:
        if host not in all_targets:
            raise HTTPException(status_code=400, detail=f"不支持的 host: {host}")
        targets = [host]
    elif auto:
        targets = detected_targets or available_targets
    else:
        targets = available_targets

    report = _collect_host_diagnostics(
        project_dir=project_dir_path,
        targets=targets,
        skill_name=skill_name,
        check_integrate=True,
        check_skill=True,
        check_slash=True,
    )
    usage_profiles = {
        target: _serialize_host_usage_profile(
            integration_manager=integration_manager,
            target=target,
        )
        for target in targets
    }
    decision_card = _build_detected_host_decision_card(
        project_dir=project_dir_path,
        integration_manager=integration_manager,
        detected_targets=detected_targets,
        detected_meta=detected_meta,
        preferred_targets=targets if host else None,
    )
    payload = _build_host_runtime_validation_payload(
        project_dir=project_dir_path,
        targets=targets,
        detected_meta=detected_meta,
        report=report,
        usage_profiles=usage_profiles,
    )

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "selected_targets": targets,
        "detected_targets": detected_targets,
        "detection_details": detected_meta,
        "detection_details_pretty": _explain_detection_details(detected_meta),
        "report": payload,
        "usage_profiles": usage_profiles,
        "decision_card": decision_card,
        "session_resume_cards": {
            target: _build_session_resume_card(project_dir_path, target, usage_profiles[target])
            for target in targets
        },
        "auto": auto,
    }


@app.get("/api/hosts/runtime-validation")
async def get_hosts_runtime_validation(
    project_dir: str = ".",
    host: str | None = None,
    auto: bool = False,
    skill_name: str = "super-dev",
) -> dict[str, Any]:
    """读取宿主真人运行时验收状态。"""
    return await validate_hosts(
        project_dir=project_dir, host=host, auto=auto, skill_name=skill_name
    )


@app.post("/api/hosts/runtime-validation", dependencies=[Depends(get_api_key)])
async def update_hosts_runtime_validation(
    request: HostRuntimeValidationRequest,
    project_dir: str = ".",
) -> dict[str, Any]:
    """更新宿主真人运行时验收状态。"""
    project_dir_path = _validate_project_dir(project_dir)
    integration_manager = IntegrationManager(project_dir_path)
    available_targets = [item.name for item in integration_manager.list_targets()]
    if request.host not in available_targets:
        raise HTTPException(status_code=400, detail=f"不支持的 host: {request.host}")

    runtime_state, file_path = _update_host_runtime_validation_state(
        project_dir=project_dir_path,
        host=request.host,
        status=request.status,
        comment=request.comment,
        actor=request.actor,
    )
    host_entry = runtime_state.get("hosts", {}).get(request.host, {})
    if not isinstance(host_entry, dict):
        host_entry = {}
    return {
        "status": "success",
        "host": request.host,
        "manual_runtime_status": request.status,
        "manual_runtime_status_label": _host_runtime_status_label(request.status),
        "comment": str(host_entry.get("comment", "")).strip(),
        "actor": str(host_entry.get("actor", "")).strip(),
        "updated_at": str(host_entry.get("updated_at", "")).strip(),
        "runtime_evidence": _build_runtime_evidence_record(
            host_id=request.host,
            surface_ready=True,
            runtime_entry=host_entry,
        ),
        "file_path": str(file_path),
    }


@app.get("/api/deploy/platforms")
async def list_deploy_platforms() -> dict:
    """列出支持的 CI/CD 平台"""
    return {"platforms": CICD_PLATFORM_CATALOG}


@app.get("/api/deploy/precheck")
async def precheck_deploy_configs(
    cicd_platform: str = "all",
    include_runtime: bool = True,
    project_dir: str = ".",
) -> dict:
    """部署生成前预检（变量与目标文件状态）。"""
    if cicd_platform not in VALID_CICD_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 cicd_platform: {cicd_platform}",
        )

    project_dir_path = _validate_project_dir(project_dir)
    target_files = _resolve_deploy_targets(cicd_platform, include_runtime)
    existing_files = [p for p in target_files if (project_dir_path / p).exists()]
    missing_files = [p for p in target_files if not (project_dir_path / p).exists()]

    env_hints = _resolve_deploy_env_hints(cicd_platform)
    env_checks = []
    for item in env_hints:
        name = item["name"]
        present = bool(os.getenv(name, "").strip())
        env_checks.append(
            {
                "name": name,
                "description": item["description"],
                "present": present,
            }
        )

    manual_requirements = _resolve_deploy_manual_hints(cicd_platform)
    missing_env = [item["name"] for item in env_checks if not item["present"]]

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "cicd_platform": cicd_platform,
        "include_runtime": include_runtime,
        "target_count": len(target_files),
        "existing_count": len(existing_files),
        "missing_count": len(missing_files),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "env_checks": env_checks,
        "missing_env": missing_env,
        "manual_requirements": manual_requirements,
        "ready_for_generate": len(missing_env) == 0,
    }


@app.get("/api/deploy/remediation")
async def get_deploy_remediation(
    cicd_platform: str = "all",
    only_missing: bool = True,
) -> dict:
    """获取部署修复建议（环境变量模板 + 平台操作指引）。"""
    if cicd_platform not in VALID_CICD_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 cicd_platform: {cicd_platform}",
        )

    remediation_items = _collect_deploy_env_items(
        cicd_platform=cicd_platform,
        only_missing=only_missing,
    )

    return {
        "status": "success",
        "cicd_platform": cicd_platform,
        "only_missing": only_missing,
        "items": remediation_items,
        "manual_requirements": _resolve_deploy_manual_hints(cicd_platform),
        "platform_guidance": _resolve_deploy_platform_guidance(cicd_platform),
    }


@app.post("/api/deploy/remediation/export", dependencies=[Depends(get_api_key)])
async def export_deploy_remediation(
    request: DeployRemediationExportRequest,
    project_dir: str = ".",
) -> dict:
    """导出部署修复模板文件（env 示例 + checklist）。"""
    if request.cicd_platform not in VALID_CICD_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 cicd_platform: {request.cicd_platform}",
        )

    project_dir_path = _validate_project_dir(project_dir)
    try:
        env_file_name = _validate_export_file_name(
            raw_name=request.env_file_name,
            field_name="env_file_name",
            default_name=".env.deploy.example",
        )
        checklist_name = _validate_export_file_name(
            raw_name=request.checklist_file_name or "",
            field_name="checklist_file_name",
            default_name=f"{request.cicd_platform}-secrets-checklist.md",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    generated = _generate_deploy_remediation_files(
        project_dir_path=project_dir_path,
        cicd_platform=request.cicd_platform,
        only_missing=request.only_missing,
        split_by_platform=request.split_by_platform,
        env_file_name=env_file_name,
        checklist_file_name=checklist_name,
    )

    env_path = generated["env_path"]
    checklist_path = generated["checklist_path"]
    remediation_items = generated["remediation_items"]

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "cicd_platform": request.cicd_platform,
        "only_missing": request.only_missing,
        "split_by_platform": request.split_by_platform,
        "env_file": {
            "file_name": env_path.name,
            "path": str(env_path),
        },
        "checklist_file": {
            "file_name": checklist_path.name,
            "path": str(checklist_path),
        },
        "items_count": len(remediation_items),
        "generated_files": generated["generated_files"],
        "per_platform_files": generated["per_platform_files"],
    }


@app.get("/api/deploy/remediation/archive")
async def download_deploy_remediation_archive(
    cicd_platform: str = "all",
    only_missing: bool = True,
    split_by_platform: bool = True,
    project_dir: str = ".",
) -> FileResponse:
    """生成并下载部署修复模板压缩包。"""
    if cicd_platform not in VALID_CICD_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 cicd_platform: {cicd_platform}",
        )

    project_dir_path = _validate_project_dir(project_dir)
    generated = _generate_deploy_remediation_files(
        project_dir_path=project_dir_path,
        cicd_platform=cicd_platform,
        only_missing=only_missing,
        split_by_platform=split_by_platform,
        env_file_name=".env.deploy.example",
        checklist_file_name=f"{cicd_platform}-secrets-checklist.md",
    )

    output_dir = project_dir_path / "output" / "deploy"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"deploy-remediation-{cicd_platform}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path_str in generated["generated_files"]:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue
            try:
                arcname = str(file_path.relative_to(project_dir_path))
            except ValueError:
                arcname = file_path.name
            zf.write(file_path, arcname=arcname)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_path.name,
    )


@app.post("/api/deploy/generate", dependencies=[Depends(get_api_key)])
async def generate_deploy_configs(
    request: DeployGenerateRequest,
    project_dir: str = ".",
) -> dict:
    """生成部署配置（CI/CD + 可选 Docker/K8s）。"""
    if request.cicd_platform not in VALID_CICD_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 cicd_platform: {request.cicd_platform}",
        )
    platform = _to_cicd_platform(request.cicd_platform)

    project_dir_path = _validate_project_dir(project_dir)
    config_manager = ConfigManager(project_dir_path)
    config = config_manager.config

    project_name = _sanitize_project_name(request.name or config.name or project_dir_path.name)
    tech_stack = {
        "platform": request.platform or config.platform,
        "frontend": request.frontend or config.frontend,
        "backend": request.backend or config.backend,
        "domain": request.domain or config.domain,
    }

    generator = CICDGenerator(
        project_dir=project_dir_path,
        name=project_name,
        tech_stack=tech_stack,
        platform=platform,
    )
    generated_files = generator.generate()

    selected_keys = _resolve_deploy_targets(
        cicd_platform=request.cicd_platform,
        include_runtime=request.include_runtime,
    )
    selected_keys = [key for key in selected_keys if key in generated_files]

    written_files: list[str] = []
    skipped_files: list[str] = []
    for relative_path in selected_keys:
        full_path = project_dir_path / relative_path
        if full_path.exists() and not request.overwrite:
            skipped_files.append(relative_path)
            continue
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(generated_files[relative_path], encoding="utf-8")
        written_files.append(relative_path)

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "project_name": project_name,
        "cicd_platform": request.cicd_platform,
        "include_runtime": request.include_runtime,
        "overwrite": request.overwrite,
        "generated_count": len(written_files),
        "skipped_count": len(skipped_files),
        "generated_files": written_files,
        "skipped_files": skipped_files,
    }


@app.get("/api/release/readiness")
async def get_release_readiness(
    project_dir: str = ".",
    verify_tests: bool = False,
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    evaluator = ReleaseReadinessEvaluator(project_dir_path)
    report = evaluator.evaluate(verify_tests=verify_tests)
    files = evaluator.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/release/proof-pack")
async def get_release_proof_pack(
    project_dir: str = ".",
    verify_tests: bool = False,
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = ProofPackBuilder(project_dir_path)
    report = builder.build(verify_tests=verify_tests)
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    payload["summary_file"] = str(files["summary"])
    return payload


@app.get("/api/governance/workflow-harness")
async def get_workflow_harness(project_dir: str = ".") -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = WorkflowHarnessBuilder(project_dir_path)
    report = builder.build()
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/governance/harnesses")
async def get_operational_harnesses(
    project_dir: str = ".",
    hook_limit: int = 20,
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = OperationalHarnessBuilder(project_dir_path)
    report = builder.build(hook_limit=max(hook_limit, 1))
    files = builder.write(report)
    payload = build_operational_harness_payload(
        project_dir_path,
        hook_limit=max(hook_limit, 1),
        write_reports=True,
    )
    payload["enabled"] = report.enabled
    payload["passed"] = report.passed
    payload["enabled_count"] = report.enabled_count
    payload["passed_count"] = report.passed_count
    payload["blockers"] = list(report.blockers)
    payload["next_actions"] = list(report.next_actions)
    payload["recent_timeline"] = list(report.recent_timeline)
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/governance/operational-harness")
async def get_operational_harness(
    project_dir: str = ".",
    hook_limit: int = 20,
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = OperationalHarnessBuilder(project_dir_path)
    report = builder.build(hook_limit=max(hook_limit, 1))
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/governance/timeline")
async def get_operational_timeline(
    project_dir: str = ".",
    limit: int = 10,
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    timeline = load_recent_operational_timeline(project_dir_path, limit=max(limit, 1))
    return {
        "project_dir": str(project_dir_path),
        "count": len(timeline),
        "timeline": timeline,
    }


@app.get("/api/governance/framework-harness")
async def get_framework_harness(project_dir: str = ".") -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = FrameworkHarnessBuilder(project_dir_path)
    report = builder.build()
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/governance/hook-harness")
async def get_hook_harness(project_dir: str = ".", limit: int = 20) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = HookHarnessBuilder(project_dir_path)
    report = builder.build(limit=max(limit, 1))
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/analyze/repo-map")
async def get_repo_map(project_dir: str = ".") -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = RepoMapBuilder(project_dir_path)
    report = builder.build()
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


@app.get("/api/analyze/impact")
async def get_impact_analysis(
    project_dir: str = ".",
    description: str = "",
    files: list[str] | None = Query(default=None),
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    analyzer = ImpactAnalyzer(project_dir_path)
    report = analyzer.build(description=description, files=files or [])
    written = analyzer.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(written["markdown"])
    payload["json_file"] = str(written["json"])
    return payload


@app.get("/api/analyze/regression-guard")
async def get_regression_guard(
    project_dir: str = ".",
    description: str = "",
    files: list[str] | None = Query(default=None),
) -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = RegressionGuardBuilder(project_dir_path)
    report = builder.build(description=description, files=files or [])
    written = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(written["markdown"])
    payload["json_file"] = str(written["json"])
    return payload


@app.get("/api/analyze/dependency-graph")
async def get_dependency_graph(project_dir: str = ".") -> dict[str, Any]:
    project_dir_path = _validate_project_dir(project_dir)
    builder = DependencyGraphBuilder(project_dir_path)
    report = builder.build()
    written = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(written["markdown"])
    payload["json_file"] = str(written["json"])
    return payload


# ==================== Memory 端点 ====================


@app.get("/api/memory")
async def list_memories(project_dir: str = ".") -> dict[str, Any]:
    """List all memory entries."""
    try:
        from super_dev.memory.store import MemoryStore

        project_dir_path = _validate_project_dir(project_dir)
        memory_dir = project_dir_path / ".super-dev" / "memory"
        store = MemoryStore(memory_dir)
        entries = store.list_all()
        return {
            "status": "success",
            "data": [
                {
                    "filename": e.filename,
                    "name": e.name,
                    "type": e.type,
                    "description": e.description,
                    "created_at": e.created_at,
                    "updated_at": e.updated_at,
                }
                for e in entries
            ],
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="memory module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/memory/{filename}")
async def get_memory(filename: str, project_dir: str = ".") -> dict[str, Any]:
    """Get a specific memory entry."""
    try:
        from super_dev.memory.store import MemoryStore

        project_dir_path = _validate_project_dir(project_dir)
        memory_dir = project_dir_path / ".super-dev" / "memory"
        store = MemoryStore(memory_dir)
        entry = store.load(filename)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Memory entry not found: {filename}")
        return {
            "status": "success",
            "data": {
                "filename": entry.filename,
                "name": entry.name,
                "type": entry.type,
                "description": entry.description,
                "content": entry.content,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
            },
        }
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=501, detail="memory module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/memory/{filename}")
async def delete_memory(filename: str, project_dir: str = ".") -> dict[str, Any]:
    """Delete a memory entry."""
    try:
        from super_dev.memory.store import MemoryStore

        project_dir_path = _validate_project_dir(project_dir)
        memory_dir = project_dir_path / ".super-dev" / "memory"
        store = MemoryStore(memory_dir)
        deleted = store.delete(filename)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Memory entry not found: {filename}")
        return {"status": "success", "data": {"filename": filename, "deleted": True}}
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=501, detail="memory module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/memory/consolidate")
async def consolidate_memories(project_dir: str = ".") -> dict[str, Any]:
    """Trigger dream consolidation."""
    try:
        from super_dev.memory.consolidator import MemoryConsolidator

        project_dir_path = _validate_project_dir(project_dir)
        memory_dir = project_dir_path / ".super-dev" / "memory"
        consolidator = MemoryConsolidator(memory_dir)
        if not consolidator.should_consolidate():
            return {
                "status": "skipped",
                "data": {"reason": "Consolidation conditions not met"},
            }
        result = consolidator.consolidate()
        return {
            "status": "success",
            "data": {
                "phase": result.phase,
                "merged_count": result.merged_count,
                "pruned_count": result.pruned_count,
                "duration_ms": result.duration_ms,
                "errors": result.errors,
            },
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="memory consolidator module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Hooks 端点 ====================


def _load_yaml_config(project_dir_path: Path) -> dict[str, Any]:
    """Load raw YAML config for hook manager initialization."""
    try:
        import yaml  # type: ignore[import-untyped]

        config_path = project_dir_path / "super-dev.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


@app.get("/api/hooks")
async def list_hooks(project_dir: str = ".") -> dict[str, Any]:
    """List configured hooks."""
    try:
        from super_dev.hooks.manager import HookManager

        project_dir_path = _validate_project_dir(project_dir)
        yaml_config = _load_yaml_config(project_dir_path)
        hook_mgr = HookManager.from_yaml_config(yaml_config, project_dir=project_dir_path)
        configured = hook_mgr.list_configured_hooks()
        return {"status": "success", "data": configured}
    except ImportError:
        raise HTTPException(status_code=501, detail="hooks module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/hooks/history")
async def get_hook_history(project_dir: str = ".", limit: int = 20) -> dict[str, Any]:
    """Return recent persisted hook execution history."""
    try:
        from super_dev.hooks.manager import HookManager

        project_dir_path = _validate_project_dir(project_dir)
        results = HookManager.load_recent_history(project_dir_path, limit=max(limit, 1))
        return {
            "status": "success",
            "data": [result.to_dict() for result in results],
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="hooks module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/hooks/test")
async def test_hook(
    event: str,
    phase: str = "",
    project_dir: str = ".",
) -> dict[str, Any]:
    """Test execute a hook event."""
    try:
        from super_dev.hooks.manager import HookManager

        project_dir_path = _validate_project_dir(project_dir)
        yaml_config = _load_yaml_config(project_dir_path)
        hook_mgr = HookManager.from_yaml_config(yaml_config, project_dir=project_dir_path)
        results = hook_mgr.execute(event, context={"test": True}, phase=phase)
        return {
            "status": "success",
            "data": [
                {
                    "hook_name": r.hook_name,
                    "event": r.event,
                    "success": r.success,
                    "blocked": r.blocked,
                    "output": r.output,
                    "error": r.error,
                    "duration_ms": r.duration_ms,
                }
                for r in results
            ],
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="hooks module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Experts (扩展) 端点 ====================


@app.get("/api/experts/{name}")
async def get_expert(name: str, project_dir: str = ".") -> dict[str, Any]:
    """Get a specific expert definition."""
    try:
        from super_dev.orchestrator.experts import EXPERT_PROFILES, ExpertRole

        name_upper = name.upper()
        try:
            role = ExpertRole(name_upper)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Unknown expert: {name}")
        profile = EXPERT_PROFILES.get(role)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Expert profile not found: {name}")
        return {
            "status": "success",
            "data": {
                "role": profile.role.value,
                "title": profile.title,
                "goal": profile.goal,
                "backstory": profile.backstory,
                "focus_areas": profile.focus_areas,
                "thinking_framework": profile.thinking_framework,
                "quality_criteria": profile.quality_criteria,
            },
        }
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=501, detail="experts module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Compact 端点 ====================


@app.get("/api/compact")
async def list_compacts(project_dir: str = ".") -> dict[str, Any]:
    """List all phase compact summaries."""
    try:
        from super_dev.orchestrator.context_compact import CompactEngine

        project_dir_path = _validate_project_dir(project_dir)
        engine = CompactEngine(project_dir_path)
        compact_dir = engine.compact_dir
        summaries: list[dict[str, Any]] = []
        if compact_dir.exists():
            for json_file in sorted(compact_dir.glob("*.json")):
                phase_name = json_file.stem
                summary = engine.load_compact(phase_name)
                if summary is not None:
                    summaries.append(
                        {
                            "phase": summary.phase,
                            "timestamp": summary.timestamp,
                            "primary_request": summary.primary_request,
                            "key_concepts_count": len(summary.key_concepts),
                            "files_count": len(summary.files_and_code),
                            "pending_tasks_count": len(summary.pending_tasks),
                        }
                    )
        return {"status": "success", "data": summaries}
    except ImportError:
        raise HTTPException(status_code=501, detail="context_compact module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/compact/{phase}")
async def get_compact(phase: str, project_dir: str = ".") -> dict[str, Any]:
    """Get a specific phase compact summary."""
    try:
        from super_dev.orchestrator.context_compact import CompactEngine

        project_dir_path = _validate_project_dir(project_dir)
        engine = CompactEngine(project_dir_path)
        summary = engine.load_compact(phase)
        if summary is None:
            raise HTTPException(
                status_code=404, detail=f"Compact summary not found for phase: {phase}"
            )
        return {"status": "success", "data": summary.to_dict()}
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=501, detail="context_compact module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Session Brief 端点 ====================


@app.get("/api/session-brief")
async def get_session_brief(project_dir: str = ".") -> dict[str, Any]:
    """Get current session brief."""
    try:
        from super_dev.session.brief import SessionBrief

        project_dir_path = _validate_project_dir(project_dir)
        sections = SessionBrief.load(project_dir_path)
        return {"status": "success", "data": sections}
    except ImportError:
        raise HTTPException(status_code=501, detail="session brief module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/session-brief/generate")
async def generate_session_brief(
    project_name: str,
    project_dir: str = ".",
) -> dict[str, Any]:
    """Generate a new session brief template."""
    try:
        from super_dev.session.brief import SessionBrief

        project_dir_path = _validate_project_dir(project_dir)
        template = SessionBrief.generate_template(project_name)
        # Parse the template into sections and save it
        sections = SessionBrief._parse_sections(template)
        saved_path = SessionBrief.save(project_dir_path, sections)
        return {
            "status": "success",
            "data": {"path": str(saved_path), "sections": sections},
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="session brief module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _mount_frontend_if_present() -> None:
    """在 API 路由注册完成后挂载前端，避免遮蔽 /api 路由。"""
    frontend_path = Path(__file__).parent / "frontend" / "dist"
    if not frontend_path.exists():
        return

    for route in app.routes:
        if getattr(route, "name", "") == "frontend":
            return

    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


# Mount v1 router
app.include_router(v1_router)

_mount_frontend_if_present()


# ==================== 主函数 ====================


def main():
    """启动 API 服务器"""
    host = os.getenv("SUPER_DEV_API_HOST", "127.0.0.1")
    port = int(os.getenv("SUPER_DEV_API_PORT", "8000"))
    reload_enabled = os.getenv("SUPER_DEV_API_RELOAD", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    uvicorn.run(
        "super_dev.web.api:app", host=host, port=port, reload=reload_enabled, log_level="info"
    )


if __name__ == "__main__":
    main()
