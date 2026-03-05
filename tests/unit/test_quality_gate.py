"""
质量门禁检查器测试
"""

from pathlib import Path

from super_dev.reviewers.quality_gate import CheckStatus, QualityCheck, QualityGateChecker


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

    def test_required_failed_check_blocks_gate_even_with_high_score(self, temp_project_dir: Path, monkeypatch):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node"},
            scenario_override="1-N+1",
        )

        failed_required = QualityCheck(
            name="安全审查",
            category="security",
            description="存在 critical 漏洞",
            status=CheckStatus.FAILED,
            score=95,
            weight=1.5,
        )
        passing_docs = QualityCheck(
            name="PRD 文档",
            category="documentation",
            description="文档完整",
            status=CheckStatus.PASSED,
            score=100,
            weight=1.0,
        )
        checks = [failed_required, passing_docs]

        monkeypatch.setattr(checker, "_check_documentation", lambda: [passing_docs])
        monkeypatch.setattr(checker, "_check_security", lambda _r: [failed_required])
        monkeypatch.setattr(checker, "_check_performance", lambda _r: [])
        monkeypatch.setattr(checker, "_check_testing", lambda: [])
        monkeypatch.setattr(checker, "_check_code_quality", lambda: [])
        monkeypatch.setattr(checker, "_calculate_total_score", lambda _c: 95)
        monkeypatch.setattr(checker, "_calculate_weighted_score", lambda _c: 95.0)
        monkeypatch.setattr(checker, "_generate_recommendations", lambda _c: [])

        result = checker.check(None)
        assert result.passed is False
        assert result.critical_failures
        assert checks[0].description in result.critical_failures[0]

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

    def test_has_pytest_config_requires_real_marker(self, temp_project_dir: Path):
        (temp_project_dir / "pyproject.toml").write_text(
            "[project]\nname='demo'\n",
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
        )
        assert checker._has_pytest_config() is False

    def test_has_pytest_config_from_pyproject_marker(self, temp_project_dir: Path):
        (temp_project_dir / "pyproject.toml").write_text(
            "[tool.pytest.ini_options]\naddopts='-q'\n",
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
        )
        assert checker._has_pytest_config() is True

    def test_discover_js_test_targets_and_run(self, temp_project_dir: Path, monkeypatch):
        frontend = temp_project_dir / "frontend"
        frontend.mkdir(parents=True, exist_ok=True)
        (frontend / "package.json").write_text(
            '{"name":"frontend","scripts":{"test":"vitest run"}}',
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "node"},
            scenario_override="1-N+1",
        )

        monkeypatch.setattr("super_dev.reviewers.quality_gate.shutil.which", lambda cmd: "/usr/bin/npm" if cmd == "npm" else None)
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
        monkeypatch.setattr(checker, "_read_coverage_percent", lambda: 85)

        checks = checker._check_testing()
        names = {c.name: c for c in checks}
        assert checker._has_js_test_script() is True
        assert names["测试执行"].status.value == "passed"

    def test_spec_task_completion_passed(self, temp_project_dir: Path):
        task_file = temp_project_dir / ".super-dev" / "changes" / "demo" / "tasks.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(
            "# Tasks\n\n- [x] **1.1: done**\n- [x] **1.2: done**\n",
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="0-1",
        )
        check = checker._check_spec_task_completion()
        assert check.status.value == "passed"
        assert check.score == 100

    def test_spec_task_completion_failed_with_pending(self, temp_project_dir: Path):
        task_file = temp_project_dir / ".super-dev" / "changes" / "demo" / "tasks.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(
            "# Tasks\n\n- [x] **1.1: done**\n- [ ] **1.2: pending**\n",
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_spec_task_completion()
        assert check.status.value == "failed"

    def test_pipeline_observability_check_passed(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-pipeline-metrics.json").write_text(
            (
                "{\n"
                '  "project_name": "demo",\n'
                '  "success": true,\n'
                '  "success_rate": 100,\n'
                '  "stages": []\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_pipeline_observability()
        assert check.status.value == "passed"

    def test_host_compatibility_check_passed(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 92.5,\n'
                '    "ready_hosts": 2,\n'
                '    "total_hosts": 3\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "passed"
        assert check.score == 92

    def test_host_compatibility_check_failed_when_score_low(self, temp_project_dir: Path):
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 48,\n'
                '    "ready_hosts": 0,\n'
                '    "total_hosts": 5\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "failed"
        assert check.score == 48

    def test_host_compatibility_check_warning_when_missing(self, temp_project_dir: Path):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="0-1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "warning"

    def test_host_compatibility_uses_config_thresholds(self, temp_project_dir: Path):
        (temp_project_dir / "super-dev.yaml").write_text(
            (
                "name: demo\n"
                "host_compatibility_min_score: 90\n"
                "host_compatibility_min_ready_hosts: 2\n"
            ),
            encoding="utf-8",
        )
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 85,\n'
                '    "ready_hosts": 1,\n'
                '    "total_hosts": 3\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "warning"
        assert "90" in check.details

    def test_host_compatibility_override_thresholds_take_precedence(self, temp_project_dir: Path):
        (temp_project_dir / "super-dev.yaml").write_text(
            (
                "name: demo\n"
                "host_compatibility_min_score: 95\n"
                "host_compatibility_min_ready_hosts: 3\n"
            ),
            encoding="utf-8",
        )
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 82,\n'
                '    "ready_hosts": 1,\n'
                '    "total_hosts": 3\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
            host_compatibility_min_score_override=80,
            host_compatibility_min_ready_hosts_override=1,
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "passed"

    def test_host_compatibility_uses_selected_host_profile(self, temp_project_dir: Path):
        (temp_project_dir / "super-dev.yaml").write_text(
            (
                "name: demo\n"
                "host_compatibility_min_score: 80\n"
                "host_compatibility_min_ready_hosts: 1\n"
                "host_profile_targets:\n"
                "  - codex-cli\n"
                "  - claude-code\n"
                "host_profile_enforce_selected: true\n"
            ),
            encoding="utf-8",
        )
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 20,\n'
                '    "ready_hosts": 0,\n'
                '    "total_hosts": 6,\n'
                '    "hosts": {\n'
                '      "codex-cli": {"score": 100, "ready": true},\n'
                '      "claude-code": {"score": 90, "ready": true},\n'
                '      "cursor": {"score": 0, "ready": false}\n'
                "    }\n"
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value == "passed"
        assert "profile=codex-cli,claude-code" in check.details

    def test_host_compatibility_selected_profile_missing_hosts(self, temp_project_dir: Path):
        (temp_project_dir / "super-dev.yaml").write_text(
            (
                "name: demo\n"
                "host_profile_targets:\n"
                "  - codex-cli\n"
                "host_profile_enforce_selected: true\n"
            ),
            encoding="utf-8",
        )
        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-host-compatibility.json").write_text(
            (
                "{\n"
                '  "compatibility": {\n'
                '    "overall_score": 100,\n'
                '    "ready_hosts": 3,\n'
                '    "total_hosts": 3,\n'
                '    "hosts": {\n'
                '      "cursor": {"score": 100, "ready": true}\n'
                "    }\n"
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_host_compatibility()
        assert check.status.value in {"warning", "failed"}

    def test_launch_rehearsal_check_warning_when_missing(self, temp_project_dir: Path):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="0-1",
        )
        check = checker._check_launch_rehearsal()
        assert check.status.value == "warning"

    def test_rehearsal_verification_report_passed(self, temp_project_dir: Path):
        rehearsal_dir = temp_project_dir / "output" / "rehearsal"
        rehearsal_dir.mkdir(parents=True, exist_ok=True)
        (rehearsal_dir / "demo-rehearsal-report.md").write_text("# report", encoding="utf-8")
        (rehearsal_dir / "demo-rehearsal-report.json").write_text('{"passed": true}', encoding="utf-8")

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_rehearsal_verification_report()
        assert check.status.value == "passed"

    def test_rehearsal_verification_report_warning_when_missing(self, temp_project_dir: Path):
        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="0-1",
        )
        check = checker._check_rehearsal_verification_report()
        assert check.status.value == "warning"

    def test_knowledge_governance_passed(self, temp_project_dir: Path):
        (temp_project_dir / "super-dev.yaml").write_text(
            (
                "name: demo\n"
                "knowledge_allowed_domains:\n"
                "  - openai.com\n"
                "knowledge_cache_ttl_seconds: 120\n"
            ),
            encoding="utf-8",
        )
        cache_dir = temp_project_dir / "output" / "knowledge-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "demo-knowledge-bundle.json").write_text(
            (
                "{\n"
                '  "cache_signature": "abc123",\n'
                '  "cache_ttl_seconds": 120,\n'
                '  "metadata": {\n'
                '    "web_enabled": true,\n'
                '    "allowed_web_domains": ["openai.com"],\n'
                '    "web_stats": {"filtered_out_count": 1}\n'
                "  }\n"
                "}\n"
            ),
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_knowledge_governance()
        assert check.status.value == "passed"

    def test_knowledge_governance_failed_when_signature_missing(self, temp_project_dir: Path):
        cache_dir = temp_project_dir / "output" / "knowledge-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "demo-knowledge-bundle.json").write_text(
            (
                "{\n"
                '  "cache_ttl_seconds": 120,\n'
                '  "metadata": {"web_enabled": false}\n'
                "}\n"
            ),
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="1-N+1",
        )
        check = checker._check_knowledge_governance()
        assert check.status.value == "failed"

    def test_knowledge_governance_warning_when_web_without_domains(self, temp_project_dir: Path):
        cache_dir = temp_project_dir / "output" / "knowledge-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "demo-knowledge-bundle.json").write_text(
            (
                "{\n"
                '  "cache_signature": "abc123",\n'
                '  "cache_ttl_seconds": 120,\n'
                '  "metadata": {"web_enabled": true, "allowed_web_domains": []}\n'
                "}\n"
            ),
            encoding="utf-8",
        )

        checker = QualityGateChecker(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"frontend": "react", "backend": "python"},
            scenario_override="0-1",
        )
        check = checker._check_knowledge_governance()
        assert check.status.value == "warning"
