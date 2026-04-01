"""PipelineCostTracker 单元测试。"""

import json

from super_dev.pipeline_cost import PhaseCost, PipelineCost, PipelineCostTracker


class TestPhaseCost:
    """PhaseCost dataclass 基本行为。"""

    def test_defaults(self):
        cost = PhaseCost(phase="discovery")
        assert cost.phase == "discovery"
        assert cost.duration_seconds == 0.0
        assert cost.files_read == 0
        assert cost.files_written == 0
        assert cost.commands_executed == 0
        assert cost.started_at == ""
        assert cost.completed_at == ""


class TestPipelineCost:
    """PipelineCost dataclass 基本行为。"""

    def test_defaults(self):
        pc = PipelineCost()
        assert pc.phases == {}
        assert pc.total_duration == 0.0
        assert pc.started_at == ""

    def test_with_phases(self):
        phases = {"discovery": PhaseCost(phase="discovery", duration_seconds=1.5)}
        pc = PipelineCost(phases=phases, total_duration=1.5, started_at="2026-01-01T00:00:00+00:00")
        assert "discovery" in pc.phases
        assert pc.total_duration == 1.5


class TestPipelineCostTracker:
    """PipelineCostTracker 核心功能。"""

    def test_start_and_end_phase(self):
        tracker = PipelineCostTracker()
        tracker.start_pipeline()
        tracker.start_phase("discovery")
        tracker.end_phase("discovery", files_read=3, files_written=1)

        summary = tracker.get_summary()
        assert "discovery" in summary.phases
        assert summary.phases["discovery"].files_read == 3
        assert summary.phases["discovery"].files_written == 1
        assert summary.phases["discovery"].duration_seconds >= 0
        assert summary.total_duration >= 0

    def test_multiple_phases(self):
        tracker = PipelineCostTracker()
        tracker.start_pipeline()

        for phase in ("discovery", "intelligence", "drafting"):
            tracker.start_phase(phase)
            tracker.end_phase(phase)

        summary = tracker.get_summary()
        assert len(summary.phases) == 3
        assert summary.started_at != ""

    def test_end_phase_without_start(self):
        """end_phase without prior start should not crash."""
        tracker = PipelineCostTracker()
        tracker.end_phase("unknown")
        summary = tracker.get_summary()
        assert "unknown" in summary.phases
        assert summary.phases["unknown"].duration_seconds == 0.0

    def test_save_and_load(self, tmp_path):
        tracker = PipelineCostTracker()
        tracker.start_pipeline()
        tracker.start_phase("qa")
        tracker.end_phase("qa", files_read=5, commands_executed=2)

        path = tracker.save(tmp_path)
        assert path.exists()

        # Verify JSON structure
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "phases" in data
        assert "qa" in data["phases"]
        assert data["phases"]["qa"]["files_read"] == 5
        assert data["total_duration"] >= 0

        # Round-trip via load
        loaded = tracker.load(tmp_path)
        assert loaded is not None
        assert "qa" in loaded.phases
        assert loaded.phases["qa"].files_read == 5
        assert loaded.phases["qa"].commands_executed == 2

    def test_load_missing(self, tmp_path):
        tracker = PipelineCostTracker()
        assert tracker.load(tmp_path) is None

    def test_load_corrupt(self, tmp_path):
        metrics_dir = tmp_path / ".super-dev" / "metrics"
        metrics_dir.mkdir(parents=True)
        (metrics_dir / "pipeline-cost.json").write_text("NOT JSON", encoding="utf-8")

        tracker = PipelineCostTracker()
        assert tracker.load(tmp_path) is None

    def test_summary_completed_at(self):
        tracker = PipelineCostTracker()
        tracker.start_pipeline()
        tracker.start_phase("delivery")
        tracker.end_phase("delivery")

        summary = tracker.get_summary()
        assert summary.completed_at != ""
