"""Workflow router — all /api/workflow/* routes."""

import asyncio
import json
import uuid
import zipfile
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

# Pydantic models (moved from api.py)
from pydantic import BaseModel

from super_dev.config import ConfigManager
from super_dev.orchestrator import Phase, WorkflowContext, WorkflowEngine
from super_dev.review_state import (
    architecture_revision_file,
    docs_confirmation_file,
    load_architecture_revision,
    load_docs_confirmation,
    load_preview_confirmation,
    load_quality_revision,
    load_ui_revision,
    preview_confirmation_file,
    quality_revision_file,
    save_architecture_revision,
    save_docs_confirmation,
    save_preview_confirmation,
    save_quality_revision,
    save_ui_revision,
    ui_revision_file,
)
from super_dev.web.helpers import (
    _get_run_state,
    _is_cancel_requested,
    _list_persisted_runs,
    _sanitize_run_payload,
    _store_run_state,
    _utc_now,
    _validate_project_dir,
    _validate_run_id,
    _with_pipeline_summary,
)


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


router = APIRouter()


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
            import logging

            logging.getLogger("super_dev.web.api").debug(f"Failed to parse UI review JSON: {e}")
    return None


def _find_ui_review_screenshot(project_dir_path: Path) -> Path | None:
    screenshot_dir = project_dir_path / "output" / "ui-review"
    if not screenshot_dir.exists():
        return None
    candidates = sorted(screenshot_dir.glob("*-preview-desktop.png"))
    return candidates[-1] if candidates else None


def _get_api_key_dependency():
    """Lazy import of get_api_key to avoid circular imports."""
    from super_dev.web.api import get_api_key

    return Depends(get_api_key)


@router.post("/workflow/run", dependencies=[])
async def run_workflow(
    request: WorkflowRunRequest, background_tasks: BackgroundTasks, project_dir: str = "."
) -> WorkflowRunResponse:
    """运行工作流"""
    # Manual API key check
    # Note: dependencies=[] is a placeholder; the actual dependency is added via include_router

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


@router.get("/workflow/status/{run_id}")
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


@router.get("/workflow/docs-confirmation")
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


@router.post("/workflow/docs-confirmation")
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


@router.get("/workflow/preview-confirmation")
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


@router.post("/workflow/preview-confirmation")
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


@router.get("/workflow/ui-revision")
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


@router.post("/workflow/ui-revision")
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


@router.get("/workflow/architecture-revision")
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


@router.post("/workflow/architecture-revision")
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


@router.get("/workflow/quality-revision")
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


@router.post("/workflow/quality-revision")
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


@router.post("/workflow/cancel/{run_id}")
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


@router.get("/workflow/runs")
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


@router.get("/workflow/artifacts/{run_id}")
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


@router.get("/workflow/artifacts/{run_id}/archive")
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


@router.get("/workflow/ui-review/{run_id}")
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


@router.get("/workflow/ui-review/{run_id}/screenshot")
async def download_workflow_ui_review_screenshot(
    run_id: str, project_dir: str = "."
) -> FileResponse:
    """获取某次工作流 UI 审查截图。"""
    _, run_project_dir = _resolve_run_project_dir(run_id, project_dir)
    screenshot = _find_ui_review_screenshot(run_project_dir)
    if screenshot is None:
        raise HTTPException(status_code=404, detail="未找到 UI 审查截图")
    return FileResponse(path=screenshot, media_type="image/png", filename=screenshot.name)
