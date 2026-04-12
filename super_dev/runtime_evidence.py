from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntegrationStatus(str, Enum):
    """Status for host integration / installation state."""

    MISSING = "missing"
    PROJECT_ONLY_INSTALLED = "project_only_installed"
    GLOBAL_ONLY_INSTALLED = "global_only_installed"
    PROJECT_AND_GLOBAL_INSTALLED = "project_and_global_installed"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class RuntimeStatus(str, Enum):
    """Status for host runtime validation state."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


def _normalize_strings(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    return tuple(item.strip() for item in values if isinstance(item, str) and item.strip())


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _coerce_integration_status(value: IntegrationStatus | str | None) -> IntegrationStatus:
    if isinstance(value, IntegrationStatus):
        return value
    raw = str(value or "").strip().lower()
    if not raw:
        return IntegrationStatus.UNKNOWN
    try:
        return IntegrationStatus(raw)
    except ValueError:
        return IntegrationStatus.UNKNOWN


def _coerce_runtime_status(value: RuntimeStatus | str | None) -> RuntimeStatus:
    if isinstance(value, RuntimeStatus):
        return value
    raw = str(value or "").strip().lower()
    if not raw:
        return RuntimeStatus.UNKNOWN
    try:
        return RuntimeStatus(raw)
    except ValueError:
        return RuntimeStatus.UNKNOWN


@dataclass(frozen=True, slots=True)
class IntegrationStatusRecord:
    """Installation / integration evidence for a host."""

    status: IntegrationStatus
    evidence: tuple[str, ...] = ()
    checked_at: str = ""
    source: str = ""
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "evidence": list(self.evidence),
            "checked_at": self.checked_at,
            "source": self.source,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> IntegrationStatusRecord:
        data = payload or {}
        return cls(
            status=_coerce_integration_status(data.get("status")),
            evidence=_normalize_strings(data.get("evidence")),
            checked_at=_normalize_text(data.get("checked_at")),
            source=_normalize_text(data.get("source")),
            details=_normalize_text(data.get("details")),
        )


@dataclass(frozen=True, slots=True)
class RuntimeStatusRecord:
    """Runtime validation evidence for a host."""

    status: RuntimeStatus
    evidence: tuple[str, ...] = ()
    checked_at: str = ""
    source: str = ""
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "evidence": list(self.evidence),
            "checked_at": self.checked_at,
            "source": self.source,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> RuntimeStatusRecord:
        data = payload or {}
        return cls(
            status=_coerce_runtime_status(data.get("status")),
            evidence=_normalize_strings(data.get("evidence")),
            checked_at=_normalize_text(data.get("checked_at")),
            source=_normalize_text(data.get("source")),
            details=_normalize_text(data.get("details")),
        )


@dataclass(frozen=True, slots=True)
class HostRuntimeEvidence:
    """Host-level evidence that keeps integration and runtime separate."""

    host_id: str
    integration_status: IntegrationStatusRecord
    runtime_status: RuntimeStatusRecord
    host_display_name: str = ""
    summary: str = ""
    evidence: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "host_display_name": self.host_display_name,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "integration_status": self.integration_status.to_dict(),
            "runtime_status": self.runtime_status.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> HostRuntimeEvidence:
        data = payload or {}
        integration_payload = data.get("integration_status")
        runtime_payload = data.get("runtime_status")
        return cls(
            host_id=_normalize_text(data.get("host_id")),
            host_display_name=_normalize_text(data.get("host_display_name")),
            summary=_normalize_text(data.get("summary")),
            evidence=_normalize_strings(data.get("evidence")),
            integration_status=IntegrationStatusRecord.from_dict(
                integration_payload if isinstance(integration_payload, dict) else {}
            ),
            runtime_status=RuntimeStatusRecord.from_dict(
                runtime_payload if isinstance(runtime_payload, dict) else {}
            ),
        )


def serialize_integration_status(record: IntegrationStatusRecord) -> dict[str, Any]:
    return record.to_dict()


def deserialize_integration_status(payload: dict[str, Any] | None) -> IntegrationStatusRecord:
    return IntegrationStatusRecord.from_dict(payload)


def serialize_runtime_status(record: RuntimeStatusRecord) -> dict[str, Any]:
    return record.to_dict()


def deserialize_runtime_status(payload: dict[str, Any] | None) -> RuntimeStatusRecord:
    return RuntimeStatusRecord.from_dict(payload)


def serialize_host_runtime_evidence(evidence: HostRuntimeEvidence) -> dict[str, Any]:
    return evidence.to_dict()


def deserialize_host_runtime_evidence(payload: dict[str, Any] | None) -> HostRuntimeEvidence:
    return HostRuntimeEvidence.from_dict(payload)


__all__ = [
    "HostRuntimeEvidence",
    "IntegrationStatus",
    "IntegrationStatusRecord",
    "RuntimeStatus",
    "RuntimeStatusRecord",
    "deserialize_host_runtime_evidence",
    "deserialize_integration_status",
    "deserialize_runtime_status",
    "serialize_host_runtime_evidence",
    "serialize_integration_status",
    "serialize_runtime_status",
]
