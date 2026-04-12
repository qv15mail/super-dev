"""
Shared helpers for Super Dev Web API routers.
"""

import fcntl
import json
import logging
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import HTTPException

_api_logger = logging.getLogger("super_dev.web.api")

# ==================== Path Security ====================


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


def _public_host_targets(*, integration_manager: Any) -> list[str]:
    from super_dev.catalogs import PRIMARY_HOST_TOOL_IDS

    available_targets = [item.name for item in integration_manager.list_targets()]
    public_targets = [target for target in PRIMARY_HOST_TOOL_IDS if target in available_targets]
    return public_targets or available_targets


# ==================== UTC Helpers ====================


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==================== Run State Helpers ====================

_RUN_STORE: dict[str, dict[str, Any]] = {}
_RUN_STORE_LOCK = Lock()
_RUN_STORE_MAX = 1000


def _evict_run_store() -> None:
    """Evict oldest in-memory run states when store exceeds max size."""
    if len(_RUN_STORE) <= _RUN_STORE_MAX:
        return
    overflow = len(_RUN_STORE) - _RUN_STORE_MAX
    keys_to_remove = list(_RUN_STORE.keys())[:overflow]
    for key in keys_to_remove:
        _RUN_STORE.pop(key, None)


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
    from super_dev.workflow_state import detect_pipeline_summary

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
