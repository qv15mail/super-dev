from __future__ import annotations

from super_dev.runtime_evidence import (
    HostRuntimeEvidence,
    IntegrationStatus,
    IntegrationStatusRecord,
    RuntimeStatus,
    RuntimeStatusRecord,
    deserialize_host_runtime_evidence,
    deserialize_integration_status,
    deserialize_runtime_status,
    serialize_host_runtime_evidence,
    serialize_integration_status,
    serialize_runtime_status,
)


def test_runtime_evidence_serialization_keeps_integration_and_runtime_separate():
    integration = IntegrationStatusRecord(
        status=IntegrationStatus.PROJECT_AND_GLOBAL_INSTALLED,
        evidence=("project setup completed", "global setup completed"),
        checked_at="2026-04-12T10:00:00+08:00",
        source="host-registry",
        details="project + global surfaces installed",
    )
    runtime = RuntimeStatusRecord(
        status=RuntimeStatus.PASSED,
        evidence=("smoke prompt passed", "resume prompt passed"),
        checked_at="2026-04-12T10:05:00+08:00",
        source="host-smoke",
        details="runtime smoke passed",
    )
    evidence = HostRuntimeEvidence(
        host_id="codebuddy",
        host_display_name="CodeBuddy IDE",
        summary="integration and runtime are independently tracked",
        evidence=("evidence pack v1",),
        integration_status=integration,
        runtime_status=runtime,
    )

    payload = serialize_host_runtime_evidence(evidence)

    assert payload["host_id"] == "codebuddy"
    assert payload["host_display_name"] == "CodeBuddy IDE"
    assert payload["summary"] == "integration and runtime are independently tracked"
    assert payload["integration_status"]["status"] == "project_and_global_installed"
    assert payload["runtime_status"]["status"] == "passed"
    assert payload["integration_status"]["evidence"] == [
        "project setup completed",
        "global setup completed",
    ]
    assert payload["runtime_status"]["evidence"] == [
        "smoke prompt passed",
        "resume prompt passed",
    ]

    restored = deserialize_host_runtime_evidence(payload)

    assert restored == evidence
    assert restored.integration_status.status is IntegrationStatus.PROJECT_AND_GLOBAL_INSTALLED
    assert restored.runtime_status.status is RuntimeStatus.PASSED


def test_status_helpers_round_trip_with_unknown_and_string_payloads():
    integration_payload = {
        "status": "manual",
        "evidence": ["manual setup"],
        "checked_at": "2026-04-12T11:00:00+08:00",
        "source": "registry",
        "details": "manual host installation",
    }
    runtime_payload = {
        "status": "blocked",
        "evidence": ["missing prompt contract"],
        "checked_at": "2026-04-12T11:01:00+08:00",
        "source": "runtime-check",
        "details": "runtime validation blocked",
    }

    integration = deserialize_integration_status(integration_payload)
    runtime = deserialize_runtime_status(runtime_payload)

    assert integration == IntegrationStatusRecord(
        status=IntegrationStatus.MANUAL,
        evidence=("manual setup",),
        checked_at="2026-04-12T11:00:00+08:00",
        source="registry",
        details="manual host installation",
    )
    assert runtime == RuntimeStatusRecord(
        status=RuntimeStatus.BLOCKED,
        evidence=("missing prompt contract",),
        checked_at="2026-04-12T11:01:00+08:00",
        source="runtime-check",
        details="runtime validation blocked",
    )

    assert serialize_integration_status(integration)["status"] == "manual"
    assert serialize_runtime_status(runtime)["status"] == "blocked"
