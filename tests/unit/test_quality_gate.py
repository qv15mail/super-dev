# -*- coding: utf-8 -*-
"""
质量门禁检查器测试
"""

from pathlib import Path

from super_dev.reviewers.quality_gate import QualityGateChecker


class TestQualityGateChecker:
    def test_scenario_override_zero_to_one(self, temp_project_dir: Path):
        # 即使存在源码目录，通过 override 仍应按 0-1 判定
        (temp_project_dir / "src").mkdir(parents=True, exist_ok=True)

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node"},
            scenario_override="0-1",
        )
        assert checker.is_zero_to_one is True

    def test_scenario_override_one_to_many(self, temp_project_dir: Path):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node"},
            scenario_override="1-N+1",
        )
        assert checker.is_zero_to_one is False

    def test_threshold_override(self, temp_project_dir: Path, monkeypatch):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node"},
            scenario_override="0-1",
            threshold_override=95,
        )

        monkeypatch.setattr(checker, "_check_documentation", lambda: [])
        monkeypatch.setattr(checker, "_check_security", lambda _r: [])
        monkeypatch.setattr(checker, "_check_performance", lambda _r: [])
        monkeypatch.setattr(checker, "_check_testing", lambda: [])
        monkeypatch.setattr(checker, "_check_code_quality", lambda: [])
        monkeypatch.setattr(checker, "_calculate_total_score", lambda _c: 90)
        monkeypatch.setattr(checker, "_calculate_weighted_score", lambda _c: 90.0)
        monkeypatch.setattr(checker, "_generate_recommendations", lambda _c: [])

        result = checker.check(None)
        assert result.passed is False

    def test_testing_check_runs_pytest(self, temp_project_dir: Path, monkeypatch):
        tests_dir = temp_project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_demo.py").write_text("def test_demo(): assert True\n", encoding="utf-8")
        (temp_project_dir / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
        )

        monkeypatch.setattr("super_dev.reviewers.quality_gate.shutil.which", lambda _: "/usr/bin/pytest")
        monkeypatch.setattr(
            checker,
            "_run_command",
            lambda cmd, timeout=120: {
                "returncode": 0,
                "stdout": "1 passed in 0.01s",
                "stderr": "",
                "timed_out": False,
            },
        )
        monkeypatch.setattr(checker, "_read_coverage_percent", lambda: 82)

        checks = checker._check_testing()
        names = {c.name: c for c in checks}
        assert names["测试执行"].status.value == "passed"
        assert names["测试覆盖率"].score == 82

    def test_testing_check_failed_when_pytest_fails(self, temp_project_dir: Path, monkeypatch):
        tests_dir = temp_project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_demo.py").write_text("def test_demo(): assert False\n", encoding="utf-8")

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
        )

        monkeypatch.setattr("super_dev.reviewers.quality_gate.shutil.which", lambda _: "/usr/bin/pytest")
        monkeypatch.setattr(
            checker,
            "_run_command",
            lambda cmd, timeout=120: {
                "returncode": 1,
                "stdout": "1 failed in 0.01s",
                "stderr": "",
                "timed_out": False,
            },
        )
        monkeypatch.setattr(checker, "_read_coverage_percent", lambda: 40)

        checks = checker._check_testing()
        names = {c.name: c for c in checks}
        assert names["测试执行"].status.value == "failed"
        assert names["测试覆盖率"].status.value == "failed"

    def test_read_coverage_percent(self, temp_project_dir: Path):
        coverage = temp_project_dir / "coverage.xml"
        coverage.write_text(
            '<?xml version="1.0" ?><coverage line-rate="0.756"></coverage>',
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
        )
        assert checker._read_coverage_percent() == 76
