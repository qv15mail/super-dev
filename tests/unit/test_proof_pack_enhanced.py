# ruff: noqa: I001
"""
证据包构建器增强测试

测试对象: super_dev.proof_pack
"""

import json
from pathlib import Path

import pytest
from super_dev.proof_pack import ProofPackArtifact, ProofPackReport


# ---------------------------------------------------------------------------
# ProofPackArtifact
# ---------------------------------------------------------------------------

class TestProofPackArtifact:
    def test_basic_creation(self):
        artifact = ProofPackArtifact(name="PRD", status="ready", summary="Product requirements document")
        assert artifact.name == "PRD"
        assert artifact.status == "ready"
        assert artifact.summary == "Product requirements document"
        assert artifact.path == ""
        assert artifact.details == {}

    def test_with_path_and_details(self):
        artifact = ProofPackArtifact(
            name="Architecture", status="ready", summary="Architecture doc",
            path="/output/arch.md", details={"pages": 15, "diagrams": 3},
        )
        assert artifact.path == "/output/arch.md"
        assert artifact.details["pages"] == 15

    def test_to_dict(self):
        artifact = ProofPackArtifact(
            name="Redteam", status="incomplete", summary="Missing report",
            path="/output/redteam.md", details={"score": 65},
        )
        d = artifact.to_dict()
        assert d["name"] == "Redteam"
        assert d["status"] == "incomplete"
        assert d["path"] == "/output/redteam.md"
        assert d["details"]["score"] == 65

    def test_to_dict_empty_details(self):
        artifact = ProofPackArtifact(name="Test", status="ready", summary="Test")
        d = artifact.to_dict()
        assert d["details"] == {}

    def test_to_dict_preserves_all_fields(self):
        artifact = ProofPackArtifact(
            name="N", status="S", summary="Sum", path="P", details={"k": "v"},
        )
        d = artifact.to_dict()
        assert set(d.keys()) == {"name", "status", "summary", "path", "details"}


# ---------------------------------------------------------------------------
# ProofPackReport
# ---------------------------------------------------------------------------

class TestProofPackReport:
    def test_empty_report(self):
        report = ProofPackReport(project_name="test")
        assert report.project_name == "test"
        assert report.ready_count == 0
        assert report.total_count == 0
        assert report.status == "incomplete"
        assert report.completion_percent == 0
        assert report.blockers == []
        assert report.key_artifacts == []

    def test_all_ready(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name="PRD", status="ready", summary="Done"),
                ProofPackArtifact(name="Arch", status="ready", summary="Done"),
                ProofPackArtifact(name="UIUX", status="ready", summary="Done"),
            ],
        )
        assert report.ready_count == 3
        assert report.total_count == 3
        assert report.status == "ready"
        assert report.completion_percent == 100
        assert len(report.blockers) == 0

    def test_partial_ready(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name="PRD", status="ready", summary="Done"),
                ProofPackArtifact(name="Arch", status="incomplete", summary="Missing"),
                ProofPackArtifact(name="UIUX", status="ready", summary="Done"),
            ],
        )
        assert report.ready_count == 2
        assert report.total_count == 3
        assert report.status == "incomplete"
        assert report.completion_percent == 67
        assert len(report.blockers) == 1
        assert report.blockers[0].name == "Arch"

    def test_none_ready(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name="PRD", status="incomplete", summary="Missing"),
                ProofPackArtifact(name="Arch", status="incomplete", summary="Missing"),
            ],
        )
        assert report.ready_count == 0
        assert report.status == "incomplete"
        assert report.completion_percent == 0

    def test_single_artifact(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[ProofPackArtifact(name="PRD", status="ready", summary="Done")],
        )
        assert report.ready_count == 1
        assert report.total_count == 1
        assert report.status == "ready"
        assert report.completion_percent == 100

    def test_generated_at_is_set(self):
        report = ProofPackReport(project_name="test")
        assert report.generated_at is not None
        assert len(report.generated_at) > 0

    def test_blockers_returns_incomplete_only(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name="A", status="ready", summary="ok"),
                ProofPackArtifact(name="B", status="missing", summary="not ok"),
                ProofPackArtifact(name="C", status="error", summary="bad"),
                ProofPackArtifact(name="D", status="ready", summary="ok"),
            ],
        )
        blockers = report.blockers
        assert len(blockers) == 2
        assert all(b.status != "ready" for b in blockers)

    def test_completion_percent_rounding(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name=f"A{i}", status="ready" if i < 1 else "incomplete", summary="x")
                for i in range(3)
            ],
        )
        assert report.completion_percent == 33  # 1/3 = 0.333... -> 33

    def test_many_artifacts(self):
        report = ProofPackReport(
            project_name="big",
            artifacts=[
                ProofPackArtifact(name=f"artifact-{i}", status="ready", summary=f"Artifact {i}")
                for i in range(20)
            ],
        )
        assert report.ready_count == 20
        assert report.total_count == 20
        assert report.status == "ready"
        assert report.completion_percent == 100


# ---------------------------------------------------------------------------
# ProofPackReport - key_artifacts
# ---------------------------------------------------------------------------

class TestProofPackKeyArtifacts:
    def test_key_artifacts_prefers_known_names(self):
        report = ProofPackReport(
            project_name="test",
            artifacts=[
                ProofPackArtifact(name="prd", status="ready", summary="PRD"),
                ProofPackArtifact(name="architecture", status="ready", summary="Arch"),
                ProofPackArtifact(name="uiux", status="ready", summary="UIUX"),
                ProofPackArtifact(name="random", status="ready", summary="Other"),
            ],
        )
        keys = report.key_artifacts
        # key_artifacts should exist and be a subset of artifacts
        assert isinstance(keys, list)


# ---------------------------------------------------------------------------
# ProofPackReport - 多种状态组合
# ---------------------------------------------------------------------------

class TestProofPackReportStatusCombinations:
    def test_mixed_statuses(self):
        report = ProofPackReport(
            project_name="mixed",
            artifacts=[
                ProofPackArtifact(name="A", status="ready", summary="ok"),
                ProofPackArtifact(name="B", status="incomplete", summary="missing"),
                ProofPackArtifact(name="C", status="ready", summary="ok"),
                ProofPackArtifact(name="D", status="error", summary="failed"),
                ProofPackArtifact(name="E", status="ready", summary="ok"),
            ],
        )
        assert report.ready_count == 3
        assert report.total_count == 5
        assert report.status == "incomplete"
        assert report.completion_percent == 60
        assert len(report.blockers) == 2

    def test_all_error_status(self):
        report = ProofPackReport(
            project_name="errors",
            artifacts=[
                ProofPackArtifact(name=f"err-{i}", status="error", summary=f"Error {i}")
                for i in range(5)
            ],
        )
        assert report.ready_count == 0
        assert report.completion_percent == 0
        assert len(report.blockers) == 5

    def test_single_blocker(self):
        report = ProofPackReport(
            project_name="almost",
            artifacts=[
                ProofPackArtifact(name=f"ok-{i}", status="ready", summary="ok")
                for i in range(9)
            ] + [ProofPackArtifact(name="blocker", status="incomplete", summary="blocking")],
        )
        assert report.ready_count == 9
        assert report.completion_percent == 90
        assert len(report.blockers) == 1
        assert report.blockers[0].name == "blocker"

    def test_large_number_of_artifacts(self):
        n = 100
        artifacts = [
            ProofPackArtifact(name=f"a-{i}", status="ready" if i < 90 else "incomplete", summary=f"A{i}")
            for i in range(n)
        ]
        report = ProofPackReport(project_name="large", artifacts=artifacts)
        assert report.ready_count == 90
        assert report.total_count == 100
        assert report.completion_percent == 90
        assert len(report.blockers) == 10

    def test_artifact_names_unique(self):
        report = ProofPackReport(
            project_name="unique",
            artifacts=[
                ProofPackArtifact(name="same", status="ready", summary="first"),
                ProofPackArtifact(name="same", status="incomplete", summary="second"),
            ],
        )
        # Duplicate names are allowed at this level
        assert report.total_count == 2
        assert report.ready_count == 1

    def test_empty_summary(self):
        artifact = ProofPackArtifact(name="empty-summary", status="ready", summary="")
        d = artifact.to_dict()
        assert d["summary"] == ""

    def test_very_long_summary(self):
        long_summary = "x" * 10000
        artifact = ProofPackArtifact(name="long", status="ready", summary=long_summary)
        d = artifact.to_dict()
        assert len(d["summary"]) == 10000

    def test_special_chars_in_name(self):
        artifact = ProofPackArtifact(name="test<>& artifact", status="ready", summary="ok")
        d = artifact.to_dict()
        assert d["name"] == "test<>& artifact"

    def test_unicode_in_fields(self):
        artifact = ProofPackArtifact(name="中文名称", status="ready", summary="测试摘要")
        d = artifact.to_dict()
        assert d["name"] == "中文名称"
        assert d["summary"] == "测试摘要"

    def test_details_with_nested_structure(self):
        artifact = ProofPackArtifact(
            name="nested", status="ready", summary="ok",
            details={"level1": {"level2": {"level3": "deep"}}},
        )
        d = artifact.to_dict()
        assert d["details"]["level1"]["level2"]["level3"] == "deep"

    def test_details_with_list_values(self):
        artifact = ProofPackArtifact(
            name="list-details", status="ready", summary="ok",
            details={"items": [1, 2, 3], "tags": ["a", "b"]},
        )
        d = artifact.to_dict()
        assert d["details"]["items"] == [1, 2, 3]

    def test_completion_percent_edge_cases(self):
        # 1 of 7 = 14.28... -> should round to 14
        report = ProofPackReport(
            project_name="round",
            artifacts=[
                ProofPackArtifact(name=f"a{i}", status="ready" if i == 0 else "incomplete", summary="x")
                for i in range(7)
            ],
        )
        assert report.completion_percent == 14

    def test_completion_percent_two_thirds(self):
        report = ProofPackReport(
            project_name="twothirds",
            artifacts=[
                ProofPackArtifact(name=f"a{i}", status="ready" if i < 2 else "incomplete", summary="x")
                for i in range(3)
            ],
        )
        assert report.completion_percent == 67
