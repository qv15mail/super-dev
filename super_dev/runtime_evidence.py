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


COMPETITION_EVIDENCE_SECTIONS: tuple[str, ...] = (
    "first_response",
    "runtime_checkpoint",
    "fallback_decision",
    "demo_path",
)

COMPETITION_EVIDENCE_MIN_CONTENT_CHARS: int = 8


def _normalize_strings(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    return tuple(item.strip() for item in values if isinstance(item, str) and item.strip())


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_competition_evidence_value(value: Any) -> Any:
    if isinstance(value, str):
        text = value.strip()
        return text if text else None
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        normalized_items = []
        for item in value:
            normalized = _normalize_competition_evidence_value(item)
            if normalized in (None, "", []):
                continue
            normalized_items.append(normalized)
        return normalized_items or None
    if isinstance(value, dict):
        normalized_mapping: dict[str, Any] = {}
        for key, item in value.items():
            key_text = _normalize_text(key)
            if not key_text:
                continue
            normalized = _normalize_competition_evidence_value(item)
            if normalized in (None, "", [], {}):
                continue
            normalized_mapping[key_text] = normalized
        return normalized_mapping or None
    return None


def normalize_competition_evidence(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    normalized: dict[str, Any] = {}
    for section in COMPETITION_EVIDENCE_SECTIONS:
        section_payload = _normalize_competition_evidence_value(payload.get(section))
        if section_payload in (None, "", [], {}):
            continue
        normalized[section] = section_payload
    return normalized


def competition_evidence_missing_sections(payload: Any) -> tuple[str, ...]:
    normalized = normalize_competition_evidence(payload)
    return tuple(section for section in COMPETITION_EVIDENCE_SECTIONS if section not in normalized)


def competition_evidence_ready(payload: Any) -> bool:
    return not competition_evidence_missing_sections(payload)


def _section_text(section_payload: Any) -> str:
    """Collect every string inside a section, joined for content-quality checks."""

    if section_payload is None:
        return ""
    if isinstance(section_payload, str):
        return section_payload.strip()
    if isinstance(section_payload, bool | int | float):
        return str(section_payload).strip()
    if isinstance(section_payload, list):
        return " ".join(_section_text(item) for item in section_payload).strip()
    if isinstance(section_payload, dict):
        parts: list[str] = []
        for value in section_payload.values():
            text = _section_text(value)
            if text:
                parts.append(text)
        return " ".join(parts).strip()
    return ""


def _template_required_keywords(template: Any, section: str) -> tuple[str, ...]:
    if not isinstance(template, dict):
        return ()
    section_template = template.get(section)
    if not isinstance(section_template, dict):
        return ()
    required = section_template.get("required")
    if not isinstance(required, list):
        return ()
    return tuple(str(item).strip() for item in required if str(item).strip())


def competition_evidence_shallow_sections(
    payload: Any,
    template: Any = None,
    *,
    min_chars: int = COMPETITION_EVIDENCE_MIN_CONTENT_CHARS,
) -> tuple[str, ...]:
    """Return present sections whose content is too thin to count as real evidence.

    A section is shallow when its aggregated text is shorter than ``min_chars``,
    or when a non-empty template ``required`` list is provided and none of its
    keywords appear as a substring of the section's aggregated text (nor vice
    versa token-wise). Missing sections are NOT reported here — use
    ``competition_evidence_missing_sections`` for presence.
    """

    normalized = normalize_competition_evidence(payload)
    shallow: list[str] = []
    for section in COMPETITION_EVIDENCE_SECTIONS:
        if section not in normalized:
            continue
        text = _section_text(normalized[section])
        if len(text) < min_chars:
            shallow.append(section)
            continue
        keywords = _template_required_keywords(template, section)
        if not keywords:
            continue
        # Bidirectional substring match: keyword in text OR text token in keyword
        tokens = [token for token in text.replace("/", " ").split() if token]
        matched = False
        for keyword in keywords:
            if keyword and keyword in text:
                matched = True
                break
            for token in tokens:
                if len(token) >= 2 and token in keyword:
                    matched = True
                    break
            if matched:
                break
        if not matched:
            shallow.append(section)
    return tuple(shallow)


def evaluate_competition_evidence(payload: Any, template: Any = None) -> dict[str, Any]:
    """Full verdict for CLI/Web: missing + shallow + effective ready flag."""

    normalized = normalize_competition_evidence(payload)
    missing = competition_evidence_missing_sections(normalized)
    shallow = competition_evidence_shallow_sections(normalized, template)
    return {
        "evidence": normalized,
        "missing": missing,
        "shallow": shallow,
        "ready": not missing and not shallow,
    }


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
    competition_evidence: dict[str, Any] = field(default_factory=dict)
    competition_evidence_ready: bool = False
    competition_evidence_missing: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "host_display_name": self.host_display_name,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "competition_evidence": self.competition_evidence,
            "competition_evidence_ready": self.competition_evidence_ready,
            "competition_evidence_missing": list(self.competition_evidence_missing),
            "integration_status": self.integration_status.to_dict(),
            "runtime_status": self.runtime_status.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> HostRuntimeEvidence:
        data = payload or {}
        integration_payload = data.get("integration_status")
        runtime_payload = data.get("runtime_status")
        normalized_competition_evidence = normalize_competition_evidence(
            data.get("competition_evidence")
        )
        return cls(
            host_id=_normalize_text(data.get("host_id")),
            host_display_name=_normalize_text(data.get("host_display_name")),
            summary=_normalize_text(data.get("summary")),
            evidence=_normalize_strings(data.get("evidence")),
            competition_evidence=normalized_competition_evidence,
            competition_evidence_ready=competition_evidence_ready(normalized_competition_evidence),
            competition_evidence_missing=competition_evidence_missing_sections(
                normalized_competition_evidence
            ),
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
    "COMPETITION_EVIDENCE_MIN_CONTENT_CHARS",
    "COMPETITION_EVIDENCE_SECTIONS",
    "HostRuntimeEvidence",
    "IntegrationStatus",
    "IntegrationStatusRecord",
    "RuntimeStatus",
    "RuntimeStatusRecord",
    "competition_evidence_missing_sections",
    "competition_evidence_ready",
    "competition_evidence_shallow_sections",
    "deserialize_host_runtime_evidence",
    "deserialize_integration_status",
    "deserialize_runtime_status",
    "evaluate_competition_evidence",
    "normalize_competition_evidence",
    "serialize_host_runtime_evidence",
    "serialize_integration_status",
    "serialize_runtime_status",
]
