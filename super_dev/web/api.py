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
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Literal, cast
from urllib.parse import urlencode

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from super_dev import __description__, __version__
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
    host_path_candidates,
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
from super_dev.integrations.manager import IntegrationManager
from super_dev.orchestrator import Phase, WorkflowContext, WorkflowEngine
from super_dev.policy import PipelinePolicy, PipelinePolicyManager
from super_dev.proof_pack import ProofPackBuilder
from super_dev.release_readiness import ReleaseReadinessEvaluator
from super_dev.review_state import (
    architecture_revision_file,
    docs_confirmation_file,
    host_runtime_validation_file,
    load_architecture_revision,
    load_docs_confirmation,
    load_host_runtime_validation,
    load_quality_revision,
    load_ui_revision,
    quality_revision_file,
    save_architecture_revision,
    save_docs_confirmation,
    save_host_runtime_validation,
    save_quality_revision,
    save_ui_revision,
    ui_revision_file,
)
from super_dev.skills import SkillManager

# ==================== 数据模型 ====================

class ProjectInitRequest(BaseModel):
    """项目初始化请求"""
    name: str
    description: str = ""
    platform: str = "web"
    frontend: str = "react"
    backend: str = "node"
    domain: str = ""
    language_preferences: list[str] = []
    quality_gate: int = 80
    host_compatibility_min_score: int = 80
    host_compatibility_min_ready_hosts: int = 1
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
    min_quality_threshold: int | None = None
    allowed_cicd_platforms: list[str] | None = None
    require_host_profile: bool | None = None
    required_hosts: list[str] | None = None
    enforce_required_hosts_ready: bool | None = None
    min_required_host_score: int | None = None


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Super Dev API",
    description=f"{__description__} - Web API",
    version=__version__
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 工作流运行状态 ====================

_RUN_STORE: dict[str, dict[str, Any]] = {}
_RUN_STORE_LOCK = Lock()

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
    _run_state_file(project_dir, run_id).write_text(
        json.dumps(run, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_persisted_run_state(project_dir: Path, run_id: str) -> dict[str, Any] | None:
    file_path = _run_state_file(project_dir, run_id)
    if not file_path.exists():
        return None
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _store_run_state(run_id: str, persist_dir: Path | None = None, **fields: Any) -> None:
    with _RUN_STORE_LOCK:
        run = _RUN_STORE.setdefault(run_id, {})
        run.update(fields)
        run["run_id"] = run_id
        run["updated_at"] = _utc_now()
        if persist_dir is not None:
            _persist_run_state(persist_dir, run_id, run)


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
        except Exception:
            data = None
        if data is not None:
            runs.append(data)
    return runs


def _has_any(patterns: list[Path]) -> bool:
    return any(path.exists() for path in patterns)


def _detect_pipeline_summary(project_dir: Path, run: dict[str, Any] | None = None) -> dict[str, Any]:
    output_dir = project_dir / "output"
    changes_dir = project_dir / ".super-dev" / "changes"

    research_done = any(output_dir.glob("*-research.md"))
    prd_done = any(output_dir.glob("*-prd.md"))
    architecture_done = any(output_dir.glob("*-architecture.md"))
    uiux_done = any(output_dir.glob("*-uiux.md"))
    docs_done = prd_done and architecture_done and uiux_done
    spec_done = any(changes_dir.glob("*/proposal.md")) and any(changes_dir.glob("*/tasks.md"))
    frontend_runtime_files = sorted(output_dir.glob("*-frontend-runtime.json"))
    frontend_runtime_passed = False
    frontend_runtime_path = ""
    if frontend_runtime_files:
        latest_frontend_runtime = max(frontend_runtime_files, key=lambda path: path.stat().st_mtime)
        frontend_runtime_path = str(latest_frontend_runtime)
        try:
            frontend_runtime_payload = json.loads(latest_frontend_runtime.read_text(encoding="utf-8"))
        except Exception:
            frontend_runtime_payload = {}
        if isinstance(frontend_runtime_payload, dict):
            frontend_runtime_passed = bool(frontend_runtime_payload.get("passed", False))
    frontend_done = frontend_runtime_passed
    backend_done = _has_any(
        [
            project_dir / "backend" / "src",
            project_dir / "backend" / "package.json",
            project_dir / "backend" / "pyproject.toml",
            project_dir / "backend" / "requirements.txt",
            project_dir / "backend" / "go.mod",
        ]
    )
    quality_done = any(output_dir.glob("*-quality-gate.md")) or any(output_dir.glob("*-ui-review.md"))

    delivery_manifest_files = sorted((output_dir / "delivery").glob("*-delivery-manifest.json")) if (output_dir / "delivery").exists() else []
    delivery_manifest_ready = False
    delivery_manifest_path = ""
    if delivery_manifest_files:
        latest_manifest = max(delivery_manifest_files, key=lambda path: path.stat().st_mtime)
        delivery_manifest_path = str(latest_manifest)
        try:
            manifest_payload = json.loads(latest_manifest.read_text(encoding="utf-8"))
        except Exception:
            manifest_payload = {}
        if isinstance(manifest_payload, dict):
            delivery_manifest_ready = str(manifest_payload.get("status", "")).strip().lower() == "ready"

    rehearsal_report_files = sorted((output_dir / "rehearsal").glob("*-rehearsal-report.json")) if (output_dir / "rehearsal").exists() else []
    rehearsal_report_passed = False
    rehearsal_report_path = ""
    if rehearsal_report_files:
        latest_rehearsal_report = max(rehearsal_report_files, key=lambda path: path.stat().st_mtime)
        rehearsal_report_path = str(latest_rehearsal_report)
        try:
            rehearsal_payload = json.loads(latest_rehearsal_report.read_text(encoding="utf-8"))
        except Exception:
            rehearsal_payload = {}
        if isinstance(rehearsal_payload, dict):
            rehearsal_report_passed = bool(rehearsal_payload.get("passed", False))

    delivery_done = delivery_manifest_ready and rehearsal_report_passed
    knowledge_cache_files = sorted((output_dir / "knowledge-cache").glob("*-knowledge-bundle.json")) if (output_dir / "knowledge-cache").exists() else []
    knowledge_summary: dict[str, Any] = {
        "enabled": bool((project_dir / "knowledge").exists()),
        "cache_exists": False,
        "cache_path": "",
        "local_hits": 0,
        "web_hits": 0,
        "top_local_sources": [],
    }
    if knowledge_cache_files:
        latest_bundle = max(knowledge_cache_files, key=lambda path: path.stat().st_mtime)
        knowledge_summary["cache_exists"] = True
        knowledge_summary["cache_path"] = str(latest_bundle)
        try:
            payload = json.loads(latest_bundle.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        if isinstance(payload, dict):
            local_knowledge = payload.get("local_knowledge", [])
            web_knowledge = payload.get("web_knowledge", [])
            if isinstance(local_knowledge, list):
                knowledge_summary["local_hits"] = len(local_knowledge)
                knowledge_summary["top_local_sources"] = [
                    str(item.get("source", ""))
                    for item in local_knowledge[:3]
                    if isinstance(item, dict) and str(item.get("source", "")).strip()
                ]
            if isinstance(web_knowledge, list):
                knowledge_summary["web_hits"] = len(web_knowledge)

    docs_confirmation = load_docs_confirmation(project_dir) or {}
    docs_confirmation_status = str(docs_confirmation.get("status", "")).strip() or "pending_review"
    docs_confirmation_comment = str(docs_confirmation.get("comment", "")).strip()
    docs_confirmation_run_id = str(docs_confirmation.get("run_id", "")).strip()
    explicit_confirmed = docs_confirmation_status == "confirmed"
    explicit_revision_requested = docs_confirmation_status == "revision_requested"
    explicit_waiting_review = docs_confirmation_status == "pending_review"
    ui_revision = load_ui_revision(project_dir) or {}
    ui_revision_status = str(ui_revision.get("status", "")).strip() or "pending_review"
    ui_revision_comment = str(ui_revision.get("comment", "")).strip()
    ui_revision_run_id = str(ui_revision.get("run_id", "")).strip()
    explicit_ui_revision_requested = ui_revision_status == "revision_requested"
    architecture_revision = load_architecture_revision(project_dir) or {}
    architecture_revision_status = str(architecture_revision.get("status", "")).strip() or "pending_review"
    architecture_revision_comment = str(architecture_revision.get("comment", "")).strip()
    architecture_revision_run_id = str(architecture_revision.get("run_id", "")).strip()
    explicit_architecture_revision_requested = architecture_revision_status == "revision_requested"
    quality_revision = load_quality_revision(project_dir) or {}
    quality_revision_status = str(quality_revision.get("status", "")).strip() or "pending_review"
    quality_revision_comment = str(quality_revision.get("comment", "")).strip()
    quality_revision_run_id = str(quality_revision.get("run_id", "")).strip()
    explicit_quality_revision_requested = quality_revision_status == "revision_requested"

    run_status = str((run or {}).get("status", "unknown"))
    run_results = cast(list[dict[str, Any]], (run or {}).get("results") or [])
    running_phase = None
    if run_status in {"running", "cancelling"}:
        completed = set(cast(list[str], (run or {}).get("completed_phases") or []))
        requested = cast(list[str], (run or {}).get("requested_phases") or [])
        running_phase = next((phase_id for phase_id in requested if phase_id not in completed), None)

    def _status(done: bool, *, waiting: bool = False, running: bool = False) -> str:
        if done:
            return "completed"
        if running:
            return "running"
        if waiting:
            return "waiting"
        return "pending"

    confirmation_done = explicit_confirmed or spec_done or frontend_done or backend_done or quality_done or delivery_done
    confirmation_waiting = docs_done and not confirmation_done

    stages = [
        {
            "id": "research",
            "name": "同类产品研究",
            "status": _status(research_done, running=running_phase in {"discovery", "intelligence"} and not research_done),
            "description": "让宿主先联网研究同类产品，并沉淀 research 文档。",
        },
        {
            "id": "core_docs",
            "name": "三份核心文档",
            "status": _status(docs_done, running=running_phase == "drafting" and not docs_done),
            "description": "生成 PRD、架构、UIUX 三份核心文档。",
        },
        {
            "id": "confirmation_gate",
            "name": "等待用户确认",
            "status": (
                "completed"
                if confirmation_done
                else ("waiting" if confirmation_waiting or explicit_revision_requested or explicit_waiting_review else "pending")
            ),
            "description": "三文档生成后，必须先向用户汇报并等待确认或修改。",
        },
        {
            "id": "spec",
            "name": "Spec 与任务清单",
            "status": _status(spec_done, running=running_phase == "drafting" and docs_done and not spec_done),
            "description": "用户确认后，创建 proposal 与 tasks.md。",
        },
        {
            "id": "frontend",
            "name": "前端实现与运行验证",
            "status": _status(frontend_done, running=running_phase == "delivery" and spec_done and not frontend_done),
            "description": "先实现前端主流程，并运行验证可演示状态。",
        },
        {
            "id": "backend",
            "name": "后端实现与联调",
            "status": _status(backend_done, running=running_phase == "delivery" and frontend_done and not backend_done),
            "description": "在前端可运行后，再进入后端、认证、数据层与联调。",
        },
        {
            "id": "quality",
            "name": "质量门禁",
            "status": _status(
                quality_done,
                running=running_phase in {"redteam", "qa"} and backend_done and not quality_done,
            ),
            "description": "执行红队审查、UI 审查与质量门禁。",
        },
        {
            "id": "delivery",
            "name": "交付与发布",
            "status": _status(
                delivery_done,
                running=running_phase == "deployment" and quality_done and not delivery_done,
            ),
            "description": "生成交付包、部署配置和审计产物。",
        },
    ]

    current_stage = next((stage for stage in stages if stage["status"] in {"running", "waiting", "pending"}), stages[-1])
    if all(stage["status"] == "completed" for stage in stages):
        current_stage = stages[-1]

    blocker = ""
    if explicit_revision_requested:
        blocker = "用户已要求修改三份核心文档，当前应先修正文档并再次提交确认。"
    elif explicit_ui_revision_requested:
        blocker = "当前存在 UI 改版请求，应先更新 output/*-uiux.md，并重新执行前端运行验证与 UI review。"
    elif explicit_architecture_revision_requested:
        blocker = "当前存在架构返工请求，应先更新 output/*-architecture.md，并同步调整实现方案与任务拆解。"
    elif explicit_quality_revision_requested:
        blocker = "当前存在质量返工请求，应先修复质量/安全问题，并重新执行 quality gate 与 release proof-pack。"
    elif confirmation_waiting:
        blocker = "三份核心文档已生成，当前必须等待用户确认或提出修改意见。"
    elif not research_done:
        blocker = "当前尚未完成同类产品研究。"
    elif not docs_done:
        blocker = "当前尚未完成 PRD、架构、UIUX 三份核心文档。"
    elif not spec_done:
        blocker = "当前尚未创建 Spec proposal 与 tasks.md。"
    elif not frontend_done:
        blocker = "当前尚未完成前端实现与运行验证。"
    elif not backend_done:
        blocker = "当前尚未完成后端实现与联调。"
    elif not quality_done:
        blocker = "当前尚未完成红队 / UI / 质量门禁。"
    elif not delivery_done:
        if not delivery_manifest_ready:
            blocker = "当前交付包仍未达到 ready 状态。"
        elif not rehearsal_report_passed:
            blocker = "当前尚未通过发布演练验证。"
        else:
            blocker = "当前尚未完成交付包与部署产物。"

    completed_count = len([stage for stage in stages if stage["status"] == "completed"])
    summary = {
        "current_stage_id": current_stage["id"],
        "current_stage_name": current_stage["name"],
        "blocker": blocker,
        "completed_count": completed_count,
        "total_count": len(stages),
        "stages": stages,
        "artifacts": {
            "research": research_done,
            "prd": prd_done,
            "architecture": architecture_done,
            "uiux": uiux_done,
            "spec": spec_done,
            "frontend": frontend_done,
            "frontend_runtime_report": frontend_runtime_path,
            "backend": backend_done,
            "quality": quality_done,
            "delivery": delivery_done,
            "delivery_manifest_ready": delivery_manifest_ready,
            "delivery_manifest_path": delivery_manifest_path,
            "rehearsal_report_passed": rehearsal_report_passed,
            "rehearsal_report_path": rehearsal_report_path,
        },
        "knowledge": knowledge_summary,
        "docs_confirmation": {
            "status": docs_confirmation_status,
            "comment": docs_confirmation_comment,
            "run_id": docs_confirmation_run_id,
            "updated_at": docs_confirmation.get("updated_at", ""),
            "actor": docs_confirmation.get("actor", ""),
            "exists": bool(docs_confirmation),
        },
        "ui_revision": {
            "status": ui_revision_status,
            "comment": ui_revision_comment,
            "run_id": ui_revision_run_id,
            "updated_at": ui_revision.get("updated_at", ""),
            "actor": ui_revision.get("actor", ""),
            "exists": bool(ui_revision),
        },
        "architecture_revision": {
            "status": architecture_revision_status,
            "comment": architecture_revision_comment,
            "run_id": architecture_revision_run_id,
            "updated_at": architecture_revision.get("updated_at", ""),
            "actor": architecture_revision.get("actor", ""),
            "exists": bool(architecture_revision),
        },
        "quality_revision": {
            "status": quality_revision_status,
            "comment": quality_revision_comment,
            "run_id": quality_revision_run_id,
            "updated_at": quality_revision.get("updated_at", ""),
            "actor": quality_revision.get("actor", ""),
            "exists": bool(quality_revision),
        },
    }

    if run_results:
        summary["phase_results_count"] = len(run_results)
    return summary


def _with_pipeline_summary(run: dict[str, Any], project_dir: Path) -> dict[str, Any]:
    enriched = dict(run)
    enriched["pipeline_summary"] = _detect_pipeline_summary(project_dir, run)
    return enriched


def _is_cancel_requested(run_id: str) -> bool:
    with _RUN_STORE_LOCK:
        run = _RUN_STORE.get(run_id)
        return bool(run and run.get("cancel_requested"))


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


def _default_host_commands(host_id: str, *, supports_slash: bool) -> dict[str, str]:
    profile = IntegrationManager(Path.cwd()).get_adapter_profile(host_id)
    trigger = str(profile.trigger_command).replace("<需求描述>", "你的需求")
    commands = {
        "setup": f"super-dev setup --host {host_id} --force --yes",
        "onboard": f"super-dev onboard --host {host_id} --force --yes",
        "doctor": f"super-dev doctor --host {host_id} --repair --force",
        "audit": f"super-dev integrate audit --target {host_id}",
        "smoke": f"super-dev integrate smoke --target {host_id}",
        "run": 'super-dev "你的需求"',
        "slash": '/super-dev "你的需求"' if supports_slash else "",
        "trigger": trigger,
    }
    commands["skill"] = "super-dev-core" if IntegrationManager.requires_skill(host_id) else ""
    return commands


def _build_host_tool_catalog_payload() -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for item in HOST_TOOL_CATALOG:
        host_id = item["id"]
        target = IntegrationManager.TARGETS.get(host_id)
        supports_slash = IntegrationManager.supports_slash(host_id)
        profile = IntegrationManager(Path.cwd()).get_adapter_profile(host_id)
        final_trigger = str(profile.trigger_command).replace("<需求描述>", "你的需求")
        payload.append(
            {
                "id": host_id,
                "name": item["name"],
                "category": HOST_TOOL_CATEGORY_MAP.get(host_id, "ide"),
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
                "observed_compatibility_surfaces": list(profile.observed_compatibility_surfaces),
                "slash_command_file": IntegrationManager.SLASH_COMMAND_FILES.get(host_id, "") if supports_slash else "",
                "supports_slash": supports_slash,
                "usage_mode": profile.usage_mode,
                "primary_entry": profile.primary_entry,
                "final_trigger": final_trigger,
                "trigger_context": profile.trigger_context,
                "usage_location": profile.usage_location,
                "requires_restart_after_onboard": profile.requires_restart_after_onboard,
                "post_onboard_steps": list(profile.post_onboard_steps),
                "usage_notes": list(profile.usage_notes),
                "smoke_test_prompt": profile.smoke_test_prompt,
                "smoke_test_steps": list(profile.smoke_test_steps),
                "smoke_success_signal": profile.smoke_success_signal,
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

        for candidate in host_path_candidates(target):
            if glob.glob(candidate):
                reasons.append(f"path:{candidate}")
                break

        if reasons:
            detected.append(target)
            details[target] = reasons
    return detected, details


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
    integration_targets = IntegrationManager.TARGETS
    skill_manager = SkillManager(project_dir)

    report: dict[str, Any] = {"hosts": {}, "overall_ready": True}
    for target in targets:
        host_report: dict[str, Any] = {
            "ready": True,
            "checks": {},
            "missing": [],
            "suggestions": [],
        }

        surface_audit: dict[str, dict[str, Any]] = {}
        for surface_key, surface_path in integration_manager.collect_managed_surface_paths(
            target=target,
            skill_name=skill_name,
        ).items():
            exists = surface_path.exists()
            audit_entry: dict[str, Any] = {
                "path": str(surface_path),
                "exists": exists,
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

        invalid_surfaces = {
            key: value
            for key, value in surface_audit.items()
            if value.get("exists") and value.get("missing_markers")
        }
        host_report["checks"]["contract"] = {
            "ok": not invalid_surfaces,
            "surfaces": surface_audit,
            "invalid_surfaces": invalid_surfaces,
        }
        if invalid_surfaces:
            host_report["ready"] = False
            host_report["missing"].append("contract")
            host_report["suggestions"].append(
                f"super-dev onboard --host {target} --force --yes"
            )

        if check_integrate:
            integration_target = integration_targets.get(target)
            integrate_files = [project_dir / item for item in integration_target.files] if integration_target else []
            integrate_ok = all(path.exists() for path in integrate_files)
            host_report["checks"]["integrate"] = {
                "ok": integrate_ok,
                "files": [str(item) for item in integrate_files],
            }
            if not integrate_ok:
                host_report["ready"] = False
                host_report["missing"].append("integrate")
                host_report["suggestions"].append(
                    f"super-dev integrate setup --target {target} --force"
                )

        if check_skill and IntegrationManager.requires_skill(target):
            skill_root = skill_manager._target_dir(target) if target in SkillManager.TARGET_PATHS else None
            skill_file = skill_root / skill_name / "SKILL.md" if skill_root else None
            skill_path = str(skill_file) if skill_file else ""
            surface_available = skill_manager.skill_surface_available(target) if skill_file else False
            skill_ok = skill_file.exists() if (skill_file and surface_available) else True
            host_report["checks"]["skill"] = {
                "ok": skill_ok,
                "file": skill_path,
                "surface_available": surface_available,
                "mode": "managed" if surface_available else "compatibility-surface-unavailable",
            }
            if surface_available and not skill_ok:
                host_report["ready"] = False
                host_report["missing"].append("skill")
                host_report["suggestions"].append(
                    f"super-dev skill install super-dev --target {target} --name {skill_name} --force"
                )

        if check_slash:
            if IntegrationManager.supports_slash(target):
                project_slash_file = IntegrationManager.resolve_slash_command_path(
                    target=target,
                    scope="project",
                    project_dir=project_dir,
                )
                global_slash_file = IntegrationManager.resolve_slash_command_path(
                    target=target,
                    scope="global",
                )
                project_ok = project_slash_file.exists() if project_slash_file else False
                global_ok = global_slash_file.exists() if global_slash_file else False
                slash_ok = project_ok or global_ok
                scope = "project" if project_ok else ("global" if global_ok else "missing")
                host_report["checks"]["slash"] = {
                    "ok": slash_ok,
                    "scope": scope,
                    "project_file": str(project_slash_file) if project_slash_file else "",
                    "global_file": str(global_slash_file) if global_slash_file else "",
                }
                if not slash_ok:
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
            host_report["preconditions"] = {
                "status": precondition_status,
                "label": precondition_label,
                "guidance": precondition_guidance if isinstance(precondition_guidance, list) else [],
                "signals": precondition_signals if isinstance(precondition_signals, dict) else {},
            }
            if precondition_status == "host-auth-required":
                host_report["suggestions"].append(
                    "若宿主报 Invalid API key provided，请先在宿主内完成 /auth 或更新宿主 API key 配置。"
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
    final_trigger = str(profile.trigger_command).replace("<需求描述>", "你的需求")
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
        "observed_compatibility_surfaces": list(profile.observed_compatibility_surfaces),
        "usage_mode": profile.usage_mode,
        "primary_entry": profile.primary_entry,
        "trigger_command": profile.trigger_command,
        "final_trigger": final_trigger,
        "trigger_context": profile.trigger_context,
        "usage_location": profile.usage_location,
        "requires_restart_after_onboard": profile.requires_restart_after_onboard,
        "restart_required_label": "是" if profile.requires_restart_after_onboard else "否",
        "post_onboard_steps": list(profile.post_onboard_steps),
        "usage_notes": list(profile.usage_notes),
        "smoke_test_prompt": profile.smoke_test_prompt,
        "smoke_test_steps": list(profile.smoke_test_steps),
        "smoke_success_signal": profile.smoke_success_signal,
        "precondition_status": profile.precondition_status,
        "precondition_label": profile.precondition_label,
        "precondition_guidance": list(profile.precondition_guidance),
        "precondition_signals": dict(profile.precondition_signals),
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
    hosts[host] = {
        "status": status,
        "comment": comment.strip(),
        "actor": actor.strip() or "user",
        "updated_at": current.get("updated_at", ""),
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
        entries.append(
            {
                "host": target,
                "surface_ready": bool(host.get("ready", False)),
                "manual_runtime_status": runtime_status,
                "manual_runtime_status_label": _host_runtime_status_label(runtime_status),
                "manual_runtime_comment": str(runtime_entry.get("comment", "")).strip(),
                "manual_runtime_actor": str(runtime_entry.get("actor", "")).strip(),
                "manual_runtime_updated_at": str(runtime_entry.get("updated_at", "")).strip(),
                "final_trigger": usage.get("final_trigger", "-"),
                "host_protocol_mode": usage.get("host_protocol_mode", "-"),
                "host_protocol_summary": usage.get("host_protocol_summary", "-"),
                "certification_label": usage.get("certification_label", "-"),
                "precondition_label": usage.get("precondition_label", "-"),
                "precondition_guidance": usage.get("precondition_guidance", []),
                "smoke_test_prompt": usage.get("smoke_test_prompt", ""),
                "smoke_success_signal": usage.get("smoke_success_signal", ""),
                "runtime_checklist": [
                    "在宿主中使用最终触发命令进入 Super Dev 流水线。",
                    "确认首轮响应明确进入 research，而不是直接开始编码。",
                    "确认真实写入 output/*-research.md、output/*-prd.md、output/*-architecture.md、output/*-uiux.md。",
                    "确认三文档完成后暂停等待用户确认，而不是直接继续实现。",
                    "确认文档确认后能继续进入 Spec、前端运行验证、后端与交付阶段。",
                ],
                "pass_criteria": [
                    "首轮响应符合 Super Dev 首轮契约。",
                    "关键文档真实落盘到项目目录。",
                    "确认门真实生效。",
                    "后续恢复路径可用。",
                ],
            }
        )

    return {
        "project_dir": str(project_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_state_file": str(host_runtime_validation_file(project_dir)),
        "runtime_state_updated_at": runtime_state.get("updated_at", ""),
        "detected_hosts": list(detected_meta.keys()),
        "detection_details": detected_meta,
        "selected_targets": targets,
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
        for pattern in ("**/*.md", "**/*.json", "**/*.html", "**/*.css", "**/*.js", "**/*.yml", "**/*.yaml", "**/*.png"):
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
    requested_project_dir = Path(project_dir).resolve()
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
        except Exception:
            pass
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


def _render_deploy_env_example(cicd_platform: str, items: list[dict[str, Any]], only_missing: bool) -> str:
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


def _build_policy_response(policy: PipelinePolicy, manager: PipelinePolicyManager) -> dict[str, Any]:
    return {
        "require_redteam": policy.require_redteam,
        "require_quality_gate": policy.require_quality_gate,
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

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": __version__}


@app.get("/api/config")
async def get_config(project_dir: str = ".") -> dict:
    """获取项目配置"""
    try:
        manager = ConfigManager(Path(project_dir))
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
        manager = PipelinePolicyManager(Path(project_dir))
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
                "description": "商业级强治理（required hosts + ready 校验）",
            },
        ]
    }


@app.put("/api/policy", response_model=PipelinePolicyResponse)
async def update_policy(
    request: PipelinePolicyUpdateRequest,
    project_dir: str = ".",
) -> dict[str, Any]:
    """更新 pipeline policy"""
    try:
        manager = PipelinePolicyManager(Path(project_dir))
        preset_name = request.preset.strip().lower() if isinstance(request.preset, str) else ""
        if preset_name:
            current = manager.build_preset(preset_name)
        else:
            current = manager.load()

        min_quality_threshold = current.min_quality_threshold
        if request.min_quality_threshold is not None:
            if request.min_quality_threshold < 0 or request.min_quality_threshold > 100:
                raise HTTPException(status_code=400, detail="min_quality_threshold 必须在 0-100 之间")
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
                raise HTTPException(status_code=400, detail="min_required_host_score 必须在 0-100 之间")
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


@app.post("/api/init")
async def init_project(request: ProjectInitRequest, project_dir: str = ".") -> dict:
    """初始化项目"""
    try:
        manager = ConfigManager(Path(project_dir))
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
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/config")
async def update_config(
    updates: dict,
    project_dir: str = "."
) -> dict:
    """更新项目配置"""
    try:
        manager = ConfigManager(Path(project_dir))
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


@app.post("/api/workflow/run")
async def run_workflow(
    request: WorkflowRunRequest,
    background_tasks: BackgroundTasks,
    project_dir: str = "."
) -> WorkflowRunResponse:
    """运行工作流"""
    try:
        project_dir_path = Path(project_dir).resolve()
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
            workflow_updates["host_compatibility_min_ready_hosts"] = request.host_compatibility_min_ready_hosts
        if request.host_profile_targets is not None:
            workflow_updates["host_profile_targets"] = request.host_profile_targets
        if request.host_profile_enforce_selected is not None:
            workflow_updates["host_profile_enforce_selected"] = request.host_profile_enforce_selected
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
                    status_code=400,
                    detail=f"无效阶段: {', '.join(invalid_phases)}"
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
                        "description": request.description if request.description is not None else config.description,
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

                all_success = all(item["success"] for item in serialized_results) if serialized_results else True
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
                _store_run_state(
                    run_id,
                    persist_dir=project_dir_path,
                    status="failed",
                    message="工作流执行异常",
                    error=str(e),
                    finished_at=_utc_now(),
                )

        def _run_workflow_background_sync() -> None:
            asyncio.run(_run_workflow_background())

        background_tasks.add_task(_run_workflow_background_sync)

        return WorkflowRunResponse(
            status="started",
            message=f"工作流已启动 (ID: {run_id})",
            run_id=run_id
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/status/{run_id}")
async def get_workflow_status(run_id: str, project_dir: str = ".") -> dict:
    """获取工作流状态"""
    project_dir_path = Path(project_dir).resolve()
    run = _get_run_state(run_id, project_dir_path)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")
    enriched = _with_pipeline_summary(run, project_dir_path)
    _store_run_state(run_id, persist_dir=project_dir_path, pipeline_summary=enriched["pipeline_summary"])
    return enriched


@app.get("/api/workflow/docs-confirmation")
async def get_workflow_docs_confirmation(project_dir: str = ".") -> dict:
    """获取三文档确认状态。"""
    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/workflow/docs-confirmation")
async def update_workflow_docs_confirmation(
    request: WorkflowDocsConfirmationRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新三文档确认状态。"""
    project_dir_path = Path(project_dir).resolve()
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


@app.get("/api/workflow/ui-revision")
async def get_workflow_ui_revision(project_dir: str = ".") -> dict:
    """获取 UI 改版状态。"""
    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/workflow/ui-revision")
async def update_workflow_ui_revision(
    request: WorkflowUIRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新 UI 改版状态。"""
    project_dir_path = Path(project_dir).resolve()
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
    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/workflow/architecture-revision")
async def update_workflow_architecture_revision(
    request: WorkflowArchitectureRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新架构返工状态。"""
    project_dir_path = Path(project_dir).resolve()
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
    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/workflow/quality-revision")
async def update_workflow_quality_revision(
    request: WorkflowQualityRevisionRequest,
    project_dir: str = ".",
    run_id: str = "",
) -> dict:
    """更新质量返工状态。"""
    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/workflow/cancel/{run_id}")
async def cancel_workflow(run_id: str, project_dir: str = ".") -> dict:
    """取消工作流运行"""
    project_dir_path = Path(project_dir).resolve()
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

    project_dir_path = Path(project_dir).resolve()
    runs = [_with_pipeline_summary(run, project_dir_path) for run in _list_persisted_runs(project_dir_path, limit=limit)]
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
async def download_workflow_ui_review_screenshot(run_id: str, project_dir: str = ".") -> FileResponse:
    """获取某次工作流 UI 审查截图。"""
    _, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    screenshot = _find_ui_review_screenshot(run_project_dir)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="未找到 UI 审查截图")
    return FileResponse(path=screenshot, media_type="image/png", filename=screenshot.name)


@app.get("/api/experts")
async def list_experts() -> dict:
    """列出可用专家"""
    return {"experts": list_expert_catalog()}


@app.post("/api/experts/{expert_id}/advice")
async def generate_expert_advice(
    expert_id: str,
    request: ExpertAdviceRequest,
    project_dir: str = ".",
) -> dict:
    """生成专家建议并写入 output 目录。"""
    expert_id = expert_id.upper()
    if not has_expert(expert_id):
        raise HTTPException(status_code=404, detail=f"未知专家: {expert_id}")

    project_dir_path = Path(project_dir).resolve()
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

    project_dir_path = Path(project_dir).resolve()
    items = list_expert_advice_history(project_dir_path, limit=limit)
    return {"items": items, "count": len(items)}


@app.get("/api/experts/advice/content")
async def get_expert_advice_content(file_name: str, project_dir: str = ".") -> dict:
    """读取某个专家建议内容。"""
    project_dir_path = Path(project_dir).resolve()
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
    skill_name: str = "super-dev-core",
    skip_integrate: bool = False,
    skip_skill: bool = False,
    skip_slash: bool = False,
    repair: bool = False,
    force: bool = False,
) -> dict:
    """诊断宿主接入状态，并返回兼容性评分。"""
    project_dir_path = Path(project_dir).resolve()
    integration_manager = IntegrationManager(project_dir_path)
    available_targets = [item.name for item in integration_manager.list_targets()]
    detected_targets, detected_meta = _detect_host_targets(available_targets)

    if host:
        if host not in available_targets:
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

    return {
        "status": "success",
        "project_dir": str(project_dir_path),
        "selected_targets": targets,
        "detected_targets": detected_targets,
        "detection_details": detected_meta,
        "report": report,
        "compatibility": compatibility,
        "usage_profiles": {
            target: _serialize_host_usage_profile(
                integration_manager=integration_manager,
                target=target,
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
    skill_name: str = "super-dev-core",
) -> dict[str, Any]:
    project_dir_path = Path(project_dir).resolve()
    integration_manager = IntegrationManager(project_dir_path)
    available_targets = [item.name for item in integration_manager.list_targets()]
    detected_targets, detected_meta = _detect_host_targets(available_targets)

    if host:
        if host not in available_targets:
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
        "report": payload,
        "usage_profiles": usage_profiles,
        "auto": auto,
    }


@app.get("/api/hosts/runtime-validation")
async def get_hosts_runtime_validation(
    project_dir: str = ".",
    host: str | None = None,
    auto: bool = False,
    skill_name: str = "super-dev-core",
) -> dict[str, Any]:
    """读取宿主真人运行时验收状态。"""
    return await validate_hosts(project_dir=project_dir, host=host, auto=auto, skill_name=skill_name)


@app.post("/api/hosts/runtime-validation")
async def update_hosts_runtime_validation(
    request: HostRuntimeValidationRequest,
    project_dir: str = ".",
) -> dict[str, Any]:
    """更新宿主真人运行时验收状态。"""
    project_dir_path = Path(project_dir).resolve()
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

    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/deploy/remediation/export")
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

    project_dir_path = Path(project_dir).resolve()
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

    project_dir_path = Path(project_dir).resolve()
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


@app.post("/api/deploy/generate")
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

    project_dir_path = Path(project_dir).resolve()
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
    project_dir_path = Path(project_dir).resolve()
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
    project_dir_path = Path(project_dir).resolve()
    builder = ProofPackBuilder(project_dir_path)
    report = builder.build(verify_tests=verify_tests)
    files = builder.write(report)
    payload = report.to_dict()
    payload["report_file"] = str(files["markdown"])
    payload["json_file"] = str(files["json"])
    return payload


def _mount_frontend_if_present() -> None:
    """在 API 路由注册完成后挂载前端，避免遮蔽 /api 路由。"""
    frontend_path = Path(__file__).parent / "frontend" / "dist"
    if not frontend_path.exists():
        return

    for route in app.routes:
        if getattr(route, "name", "") == "frontend":
            return

    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


_mount_frontend_if_present()


# ==================== 主函数 ====================

def main():
    """启动 API 服务器"""
    host = os.getenv("SUPER_DEV_API_HOST", "127.0.0.1")
    port = int(os.getenv("SUPER_DEV_API_PORT", "8000"))
    reload_enabled = os.getenv("SUPER_DEV_API_RELOAD", "true").strip().lower() in {"1", "true", "yes", "on"}
    uvicorn.run(
        "super_dev.web.api:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level="info"
    )


if __name__ == "__main__":
    main()
