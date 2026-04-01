"""OnboardingGuide 单元测试。"""

import json
from unittest.mock import MagicMock

from super_dev.onboarding import OnboardingGuide


class TestOnboardingGuide:
    """OnboardingGuide 核心功能测试。"""

    def test_should_show_fresh_project(self, tmp_path):
        guide = OnboardingGuide()
        assert guide.should_show(tmp_path) is True

    def test_should_show_after_completed(self, tmp_path):
        guide = OnboardingGuide()
        guide.mark_completed(tmp_path)
        assert guide.should_show(tmp_path) is False

    def test_should_show_after_max_seen(self, tmp_path):
        guide = OnboardingGuide()
        for _ in range(OnboardingGuide.MAX_SHOW_COUNT):
            guide.mark_seen(tmp_path)
        assert guide.should_show(tmp_path) is False

    def test_mark_seen_increments(self, tmp_path):
        guide = OnboardingGuide()
        guide.mark_seen(tmp_path)
        guide.mark_seen(tmp_path)

        state = json.loads(guide._state_path(tmp_path).read_text(encoding="utf-8"))
        assert state["seen_count"] == 2

    def test_show_with_rich_console(self, tmp_path):
        guide = OnboardingGuide()
        console = MagicMock()
        guide.show(console)
        assert console.print.called

    def test_show_without_rich(self, tmp_path, capsys):
        guide = OnboardingGuide()
        # Pass a plain object without .print to trigger fallback
        guide.show(object())
        captured = capsys.readouterr()
        assert "Quick Start" in captured.out

    def test_state_persists_across_instances(self, tmp_path):
        guide1 = OnboardingGuide()
        guide1.mark_seen(tmp_path)
        guide1.mark_seen(tmp_path)

        guide2 = OnboardingGuide()
        # seen_count is 2, still below MAX_SHOW_COUNT (4)
        assert guide2.should_show(tmp_path) is True

        guide2.mark_seen(tmp_path)
        guide2.mark_seen(tmp_path)
        # now at 4
        assert guide2.should_show(tmp_path) is False

    def test_corrupt_state_file(self, tmp_path):
        state_dir = tmp_path / ".super-dev"
        state_dir.mkdir(parents=True)
        (state_dir / "onboarding.json").write_text("INVALID", encoding="utf-8")

        guide = OnboardingGuide()
        # Should not crash, treat as fresh
        assert guide.should_show(tmp_path) is True

    def test_mark_completed_persists(self, tmp_path):
        guide = OnboardingGuide()
        guide.mark_completed(tmp_path)

        state = json.loads(guide._state_path(tmp_path).read_text(encoding="utf-8"))
        assert state["completed"] is True
