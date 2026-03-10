from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def review_state_dir(project_dir: Path) -> Path:
    return Path(project_dir).resolve() / ".super-dev" / "review-state"


def docs_confirmation_file(project_dir: Path) -> Path:
    return review_state_dir(project_dir) / "document-confirmation.json"


def ui_revision_file(project_dir: Path) -> Path:
    return review_state_dir(project_dir) / "ui-revision.json"


def architecture_revision_file(project_dir: Path) -> Path:
    return review_state_dir(project_dir) / "architecture-revision.json"


def quality_revision_file(project_dir: Path) -> Path:
    return review_state_dir(project_dir) / "quality-revision.json"


def host_runtime_validation_file(project_dir: Path) -> Path:
    return review_state_dir(project_dir) / "host-runtime-validation.json"


def load_docs_confirmation(project_dir: Path) -> dict[str, Any] | None:
    file_path = docs_confirmation_file(project_dir)
    if not file_path.exists():
        return None
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_ui_revision(project_dir: Path) -> dict[str, Any] | None:
    file_path = ui_revision_file(project_dir)
    if not file_path.exists():
        return None
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_architecture_revision(project_dir: Path) -> dict[str, Any] | None:
    file_path = architecture_revision_file(project_dir)
    if not file_path.exists():
        return None
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_quality_revision(project_dir: Path) -> dict[str, Any] | None:
    file_path = quality_revision_file(project_dir)
    if not file_path.exists():
        return None
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_host_runtime_validation(project_dir: Path) -> dict[str, Any] | None:
    file_path = host_runtime_validation_file(project_dir)
    if not file_path.exists():
        return None
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def save_docs_confirmation(project_dir: Path, payload: dict[str, Any]) -> Path:
    state_dir = review_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    normalized = dict(payload)
    normalized["updated_at"] = _utc_now()
    file_path = docs_confirmation_file(project_dir)
    file_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def save_ui_revision(project_dir: Path, payload: dict[str, Any]) -> Path:
    state_dir = review_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    normalized = dict(payload)
    normalized["updated_at"] = _utc_now()
    file_path = ui_revision_file(project_dir)
    file_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def save_architecture_revision(project_dir: Path, payload: dict[str, Any]) -> Path:
    state_dir = review_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    normalized = dict(payload)
    normalized["updated_at"] = _utc_now()
    file_path = architecture_revision_file(project_dir)
    file_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def save_quality_revision(project_dir: Path, payload: dict[str, Any]) -> Path:
    state_dir = review_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    normalized = dict(payload)
    normalized["updated_at"] = _utc_now()
    file_path = quality_revision_file(project_dir)
    file_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def save_host_runtime_validation(project_dir: Path, payload: dict[str, Any]) -> Path:
    state_dir = review_state_dir(project_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    normalized = dict(payload)
    normalized["updated_at"] = _utc_now()
    file_path = host_runtime_validation_file(project_dir)
    file_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path
