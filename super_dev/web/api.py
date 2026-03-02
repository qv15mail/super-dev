#!/usr/bin/env python3
"""
开发：Excellent（11964948@qq.com）
功能：Super Dev Web API - FastAPI 后端
作用：提供 REST API 服务，支持项目管理和工作流执行
创建时间：2025-12-30
最后修改：2025-12-30
"""

import asyncio
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Literal, cast

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
from super_dev.orchestrator import Phase, WorkflowContext, WorkflowEngine

# ==================== 数据模型 ====================

class ProjectInitRequest(BaseModel):
    """项目初始化请求"""
    name: str
    description: str = ""
    platform: str = "web"
    frontend: str = "react"
    backend: str = "node"
    domain: str = ""
    quality_gate: int = 80


class ProjectConfigResponse(BaseModel):
    """项目配置响应"""
    name: str
    description: str
    version: str
    platform: str
    frontend: str
    backend: str
    domain: str
    quality_gate: int
    phases: list[str]
    experts: list[str]


class WorkflowRunRequest(BaseModel):
    """工作流运行请求"""
    phases: list[str] | None = None
    quality_gate: int | None = None
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


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="Super Dev API",
    description="顶级 AI 开发战队 - Web API",
    version="2.0.1"
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
VALID_CICD_PLATFORMS: set[str] = {"github", "gitlab", "jenkins", "azure", "bitbucket", "all"}

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
        for platform in ("github", "gitlab", "azure", "bitbucket"):
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
        for platform in ("jenkins",):
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
        for pattern in ("**/*.md", "**/*.json", "**/*.html", "**/*.css", "**/*.js", "**/*.yml", "**/*.yaml"):
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


def _resolve_deploy_platform_guidance(cicd_platform: str) -> list[str]:
    if cicd_platform == "all":
        merged: list[str] = []
        seen = set()
        for platform in ("github", "gitlab", "jenkins", "azure", "bitbucket"):
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
        for platform in ("github", "gitlab", "jenkins", "azure", "bitbucket"):
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


# ==================== API 路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "2.0.1"}


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
            "quality_gate": config.quality_gate,
            "phases": config.phases,
            "experts": config.experts,
            "output_dir": config.output_dir,
        }
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
            quality_gate=request.quality_gate
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

        # 更新质量门禁
        if request.quality_gate is not None:
            manager.update(quality_gate=request.quality_gate)
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
                        "cicd": request.cicd or "github",
                        "orm": request.orm,
                        "offline": request.offline,
                        "quality_threshold": request.quality_gate,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/status/{run_id}")
async def get_workflow_status(run_id: str, project_dir: str = ".") -> dict:
    """获取工作流状态"""
    run = _get_run_state(run_id, Path(project_dir).resolve())
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")
    return run


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
    runs = _list_persisted_runs(project_dir_path, limit=limit)
    return {"runs": runs, "count": len(runs)}


@app.get("/api/workflow/artifacts/{run_id}")
async def list_workflow_artifacts(run_id: str, project_dir: str = ".") -> dict:
    """列出某次工作流可下载的交付物文件。"""
    requested_project_dir = Path(project_dir).resolve()
    run = _get_run_state(run_id, requested_project_dir)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")

    run_project_dir = Path(run.get("project_dir") or requested_project_dir).resolve()
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
    requested_project_dir = Path(project_dir).resolve()
    run = _get_run_state(run_id, requested_project_dir)
    if run is None:
        raise HTTPException(status_code=404, detail=f"运行记录不存在: {run_id}")

    run_project_dir = Path(run.get("project_dir") or requested_project_dir).resolve()
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


@app.get("/api/deploy/platforms")
async def list_deploy_platforms() -> dict:
    """列出支持的 CI/CD 平台"""
    return {
        "platforms": [
            {"id": "all", "name": "全部平台"},
            {"id": "github", "name": "GitHub Actions"},
            {"id": "gitlab", "name": "GitLab CI"},
            {"id": "jenkins", "name": "Jenkins"},
            {"id": "azure", "name": "Azure DevOps"},
            {"id": "bitbucket", "name": "Bitbucket Pipelines"},
        ]
    }


@app.get("/api/deploy/precheck")
async def precheck_deploy_configs(
    cicd_platform: str = "all",
    include_runtime: bool = True,
    project_dir: str = ".",
) -> dict:
    """部署生成前预检（变量与目标文件状态）。"""
    valid_platforms = {"github", "gitlab", "jenkins", "azure", "bitbucket", "all"}
    if cicd_platform not in valid_platforms:
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
    valid_platforms = {"github", "gitlab", "jenkins", "azure", "bitbucket", "all"}
    if cicd_platform not in valid_platforms:
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
    valid_platforms = {"github", "gitlab", "jenkins", "azure", "bitbucket", "all"}
    if request.cicd_platform not in valid_platforms:
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
    valid_platforms = {"github", "gitlab", "jenkins", "azure", "bitbucket", "all"}
    if cicd_platform not in valid_platforms:
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
