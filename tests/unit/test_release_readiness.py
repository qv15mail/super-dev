import json
from pathlib import Path

from super_dev import __version__
from super_dev.hooks.manager import HookManager
from super_dev.release_readiness import ReleaseReadinessEvaluator
from super_dev.review_state import save_workflow_state, workflow_event_log_file
from super_dev.specs.generator import SpecGenerator


def _prepare_release_ready_project(project_dir: Path) -> None:
    (project_dir / "super_dev").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "output").mkdir(parents=True, exist_ok=True)
    (project_dir / ".super-dev" / "changes" / "release-hardening-finalization").mkdir(
        parents=True,
        exist_ok=True,
    )
    (project_dir / "pyproject.toml").write_text(f'[project]\nversion = "{__version__}"\n[project.scripts]\nsuper-dev = "super_dev.cli:main"\n', encoding="utf-8")
    (project_dir / ".gitignore").write_text(
        "\n".join(
            [
                "output/",
                "artifacts/",
                ".super-dev/runs/",
                ".super-dev/review-state/",
                "/.agent/",
                "/.claude/",
                "/.codebuddy/",
                "/.cursor/",
                "/.gemini/",
                "/.iflow/",
                "/.kimi/",
                "/.kiro/",
                "/.opencode/",
                "/.qoder/",
                "/.trae/",
                "/.windsurf/",
                "/GEMINI.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / "super_dev" / "__init__.py").write_text(f'__version__ = "{__version__}"\n', encoding="utf-8")
    (project_dir / "README.md").write_text(
        f"当前版本：`{__version__}`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "README_EN.md").write_text(
        f"Current version: `{__version__}`\npip install -U super-dev\nuv tool install super-dev\n/super-dev\nsuper-dev:\nsuper-dev update\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_USAGE_GUIDE.md").write_text(
        "Smoke\n/super-dev\nsuper-dev:\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_CAPABILITY_AUDIT.md").write_text(
        "官方依据\nsuper-dev integrate smoke\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_RUNTIME_VALIDATION.md").write_text(
        "host runtime validation\nresearch\nsuper-dev review docs\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "HOST_INSTALL_SURFACES.md").write_text(
        "Codex CLI\nsuper-dev:\nsuper-dev integrate audit --auto\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "README.md").write_text("用户文档\n维护者文档\n", encoding="utf-8")
    (project_dir / "docs" / "WORKFLOW_GUIDE.md").write_text(
        "super-dev review docs\nsuper-dev run --resume\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "WORKFLOW_GUIDE_EN.md").write_text(
        "super-dev review docs\nsuper-dev run --resume\n",
        encoding="utf-8",
    )
    (project_dir / "docs" / "PRODUCT_AUDIT.md").write_text(
        "super-dev product-audit\nproof-pack\nrelease readiness\n",
        encoding="utf-8",
    )
    (project_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    for name in ("change.yaml", "proposal.md", "tasks.md"):
        (project_dir / ".super-dev" / "changes" / "release-hardening-finalization" / name).write_text(
            "ok\n",
            encoding="utf-8",
        )
    (project_dir / "output" / f"{project_dir.name}-redteam.json").write_text(
        (
            "{\n"
            f'  "project_name": "{project_dir.name}",\n'
            '  "pass_threshold": 70,\n'
            '  "critical_count": 0,\n'
            '  "high_count": 0,\n'
            '  "total_score": 92,\n'
            '  "passed": true,\n'
            '  "blocking_reasons": [],\n'
            '  "security_issues": [],\n'
            '  "performance_issues": [],\n'
            '  "architecture_issues": []\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-quality-gate.md").write_text(
        "# 质量门禁报告\n\n**状态**: <span style='color:green'>通过</span>\n**总分**: 90/100\n",
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-task-execution.md").write_text(
        (
            "# Spec 任务执行报告\n\n"
            "## 执行期验证摘要\n\n"
            "- 构建检查已完成\n\n"
            "## 宿主补充自检（交付前必做）\n\n"
            "- 新增函数、方法、字段、模块都已接入真实调用链\n"
        ),
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-product-audit.json").write_text(
        '{\n  "status": "ready",\n  "score": 90\n}\n',
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-ui-contract.json").write_text(
        (
            "{\n"
            '  "style_direction": "Editorial workspace",\n'
            '  "typography": {"heading": "Space Grotesk", "body": "Inter"},\n'
            '  "icon_system": "lucide-react",\n'
            '  "emoji_policy": {"allowed_in_ui": false, "allowed_as_icon": false, "allowed_during_development": false},\n'
            '  "ui_library_preference": {\n'
            '    "preferred": "shadcn/ui + Radix + Tailwind",\n'
            '    "strict": false,\n'
            '    "final_selected": "shadcn/ui + Radix + Tailwind"\n'
            "  },\n"
            '  "design_tokens": {"color": {"primary": "#0f172a"}}\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    (project_dir / "output" / "frontend").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "frontend" / "design-tokens.css").write_text(
        ":root { --color-primary: #0f172a; }\n",
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-frontend-runtime.json").write_text(
        (
            "{\n"
            '  "passed": true,\n'
            '  "checks": {\n'
            '    "output_frontend_index": true,\n'
            '    "output_frontend_styles": true,\n'
            '    "output_frontend_design_tokens": true,\n'
            '    "output_frontend_script": true,\n'
            '    "preview_html": true,\n'
            '    "ui_contract_json": true,\n'
            '    "ui_contract_alignment": true,\n'
            '    "ui_theme_entry": true,\n'
            '    "ui_navigation_shell": true,\n'
            '    "ui_component_imports": true,\n'
            '    "ui_banned_patterns": true\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )
    # 治理证据 mock（确保治理检查项通过）
    (project_dir / "output" / "governance-report-test.md").write_text(
        "# Pipeline 治理报告\n\n**状态**: PASSED\n",
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-knowledge-references.json").write_text(
        '{"referenced_files": 5, "hit_rate": 0.65}\n',
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-metrics.json").write_text(
        '{"quality_gate_score": 90}\n',
        encoding="utf-8",
    )
    (project_dir / "output" / f"{project_dir.name}-validation-results.json").write_text(
        '{"passed": true, "score": 95}\n',
        encoding="utf-8",
    )
    (project_dir / "docs" / "adr").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "adr" / "ADR-001.md").write_text(
        "# ADR-001: 选择 PostgreSQL\n\n## 决策\n使用 PostgreSQL。\n",
        encoding="utf-8",
    )


def _prepare_spec_quality_change(project_dir: Path, change_id: str = "add-proof-ready") -> None:
    generator = SpecGenerator(project_dir)
    generator.init_sdd()
    change = generator.create_change(
        change_id=change_id,
        title="Add Proof Ready",
        description="用于发布前 spec 质量验证",
    )
    generator.scaffold_change_artifacts(change.id)


def test_release_readiness_detects_missing_docs(temp_project_dir: Path) -> None:
    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    assert report.passed is False
    assert "Documentation Coverage" in report.failed_checks or any(
        check.name == "Documentation Coverage" and not check.passed for check in report.checks
    )


def test_release_readiness_passes_when_required_artifacts_exist(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    _prepare_spec_quality_change(temp_project_dir)

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)
    files = evaluator.write(report)

    assert report.passed is True
    assert report.score == 100
    assert files["markdown"].exists()
    assert files["json"].exists()
    operational_check = next(
        check for check in report.checks if check.name == "Operational Harness Trail"
    )
    assert operational_check.passed is True
    assert operational_check.detail in {
        "operational harness clean across 3/3 enabled harnesses",
        "no operational harness evidence required",
    }


def test_release_readiness_fails_when_latest_spec_quality_is_weak(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    generator = SpecGenerator(temp_project_dir)
    generator.init_sdd()
    change = generator.create_change(
        change_id="weak-change",
        title="Weak Change",
        description="弱规格",
    )
    change_dir = temp_project_dir / ".super-dev" / "changes" / change.id
    (change_dir / "tasks.md").write_text("# Tasks\n\n", encoding="utf-8")

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    spec_check = next(check for check in report.checks if check.name == "Spec Quality")
    assert spec_check.passed is False
    assert "weak-change" in spec_check.detail


def test_release_readiness_fails_when_delivery_closure_is_incomplete(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    (temp_project_dir / "output" / f"{temp_project_dir.name}-task-execution.md").unlink()

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "task execution missing" in closure_check.detail


def test_release_readiness_fails_when_ui_contract_closure_is_incomplete(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    (temp_project_dir / "output" / f"{temp_project_dir.name}-ui-contract.json").unlink()

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "ui contract missing" in closure_check.detail


def test_release_readiness_fails_when_frontend_runtime_structural_ui_checks_fail(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    runtime_file = temp_project_dir / "output" / f"{temp_project_dir.name}-frontend-runtime.json"
    runtime_file.write_text(
        (
            "{\n"
            '  "passed": true,\n'
            '  "checks": {\n'
            '    "output_frontend_index": true,\n'
            '    "output_frontend_styles": true,\n'
            '    "output_frontend_design_tokens": true,\n'
            '    "output_frontend_script": true,\n'
            '    "preview_html": true,\n'
            '    "ui_contract_json": true,\n'
            '    "ui_contract_alignment": true,\n'
            '    "ui_theme_entry": false,\n'
            '    "ui_navigation_shell": true,\n'
            '    "ui_component_imports": true,\n'
            '    "ui_banned_patterns": true\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "frontend runtime ui contract alignment missing" in closure_check.detail


def test_release_readiness_fails_when_cross_platform_runtime_missing_framework_execution(
    temp_project_dir: Path,
) -> None:
    _prepare_release_ready_project(temp_project_dir)
    contract_file = temp_project_dir / "output" / f"{temp_project_dir.name}-ui-contract.json"
    payload = json.loads(contract_file.read_text(encoding="utf-8"))
    payload["analysis"] = {"frontend": "uni-app"}
    payload["framework_playbook"] = {
        "framework": "uni-app",
        "implementation_modules": ["自定义导航栏高度"],
        "platform_constraints": ["status bar 与安全区"],
        "execution_guardrails": ["先冻结 navigationStyle"],
        "native_capabilities": ["登录 provider"],
        "validation_surfaces": ["微信小程序导航"],
        "delivery_evidence": ["三端差异说明"],
    }
    contract_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    runtime_file = temp_project_dir / "output" / f"{temp_project_dir.name}-frontend-runtime.json"
    runtime_file.write_text(
        (
            "{\n"
            '  "passed": false,\n'
            '  "checks": {\n'
            '    "output_frontend_index": true,\n'
            '    "output_frontend_styles": true,\n'
            '    "output_frontend_design_tokens": true,\n'
            '    "output_frontend_script": true,\n'
            '    "preview_html": true,\n'
            '    "ui_contract_json": true,\n'
            '    "ui_contract_alignment": true,\n'
            '    "ui_theme_entry": true,\n'
            '    "ui_navigation_shell": true,\n'
            '    "ui_component_imports": true,\n'
            '    "ui_banned_patterns": true,\n'
            '    "ui_framework_playbook": true,\n'
            '    "ui_framework_execution": false\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "uni-app frontend runtime framework execution missing" in closure_check.detail


def test_release_readiness_fails_when_ui_contract_missing_emoji_policy(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    contract_file = temp_project_dir / "output" / f"{temp_project_dir.name}-ui-contract.json"
    payload = json.loads(contract_file.read_text(encoding="utf-8"))
    payload.pop("emoji_policy", None)
    contract_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "ui contract incomplete" in closure_check.detail


def test_release_readiness_fails_when_cross_platform_ui_contract_missing_framework_playbook(
    temp_project_dir: Path,
) -> None:
    _prepare_release_ready_project(temp_project_dir)
    contract_file = temp_project_dir / "output" / f"{temp_project_dir.name}-ui-contract.json"
    payload = json.loads(contract_file.read_text(encoding="utf-8"))
    payload["analysis"] = {"frontend": "uni-app"}
    contract_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    closure_check = next(check for check in report.checks if check.name == "Delivery Closure")
    assert closure_check.passed is False
    assert "uni-app ui contract playbook incomplete" in closure_check.detail


def test_release_readiness_fails_when_active_workflow_recovery_trail_is_incomplete(
    temp_project_dir: Path,
) -> None:
    _prepare_release_ready_project(temp_project_dir)
    save_workflow_state(
        temp_project_dir,
        {
            "status": "waiting_docs_confirmation",
            "workflow_mode": "continue",
            "current_step_label": "等待三文档确认",
            "recommended_command": "super-dev review docs --status confirmed",
        },
    )
    workflow_event_log_file(temp_project_dir).unlink()

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    continuity_check = next(check for check in report.checks if check.name == "Workflow Recovery Trail")
    assert continuity_check.passed is False
    assert "workflow recovery trail incomplete" in continuity_check.detail


def test_release_readiness_fails_when_hook_audit_contains_blocked_event(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    history_file = HookManager.hook_history_file(temp_project_dir)
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.write_text(
        json.dumps(
            {
                "hook_name": "python3 scripts/guard.py",
                "event": "WorkflowEvent",
                "success": False,
                "output": "",
                "error": "blocked by policy",
                "duration_ms": 8.4,
                "blocked": True,
                "phase": "quality_revision_saved",
                "source": "config",
                "timestamp": "2026-04-06T01:02:03+00:00",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    hook_check = next(check for check in report.checks if check.name == "Hook Audit Trail")
    assert hook_check.passed is False
    assert "blocked events" in hook_check.detail
    markdown = report.to_markdown()
    assert "## Operational Continuity" in markdown
    assert "## Current Governance Focus" in markdown
    assert "## Recent Operational Timeline" in markdown
    assert "Operational Harness Trail" in markdown
    assert "Workflow Recovery Trail" in markdown
    assert "Framework Harness Trail" in markdown
    assert "Hook Audit Trail" in markdown


def test_release_readiness_fails_when_framework_harness_has_blockers(
    temp_project_dir: Path,
) -> None:
    _prepare_release_ready_project(temp_project_dir)

    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{temp_project_dir.name}-ui-contract.json").write_text(
        json.dumps(
            {
                "analysis": {"frontend": "uni-app"},
                "framework_playbook": {
                    "framework": "uni-app",
                    "implementation_modules": ["pages", "composables"],
                    "native_capabilities": [],
                    "validation_surfaces": ["微信小程序导航/支付/触控与包体策略"],
                    "delivery_evidence": ["跨端截图"],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    framework_check = next(
        check for check in report.checks if check.name == "Framework Harness Trail"
    )
    assert framework_check.passed is False
    assert "uni-app harness has" in framework_check.detail


def test_release_readiness_fails_when_operational_harness_has_blockers(
    temp_project_dir: Path,
) -> None:
    _prepare_release_ready_project(temp_project_dir)

    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{temp_project_dir.name}-ui-contract.json").write_text(
        json.dumps(
            {
                "analysis": {"frontend": "uni-app"},
                "framework_playbook": {
                    "framework": "uni-app",
                    "implementation_modules": ["pages"],
                    "native_capabilities": [],
                    "validation_surfaces": ["微信小程序导航"],
                    "delivery_evidence": ["跨端截图"],
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    operational_check = next(
        check for check in report.checks if check.name == "Operational Harness Trail"
    )
    assert operational_check.passed is False
    assert "需要先处理" in operational_check.detail


def test_release_readiness_fails_when_latest_spec_contains_tbd_placeholders(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    _prepare_spec_quality_change(temp_project_dir, change_id="placeholder-change")

    spec_file = next((temp_project_dir / ".super-dev" / "changes" / "placeholder-change" / "specs").rglob("spec.md"))
    spec_file.write_text(
        "# Placeholder Change\n\n## Requirements\n\n### Requirement: Example\n\nSHALL keep placeholder\n\n#### Scenario 1: TBD\n- DETAIL REQUIRED\n",
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    spec_check = next(check for check in report.checks if check.name == "Spec Quality")
    assert spec_check.passed is False
    assert "placeholder-change" in spec_check.detail


def test_release_readiness_fails_when_scope_coverage_has_high_priority_gap(temp_project_dir: Path) -> None:
    _prepare_release_ready_project(temp_project_dir)
    output_dir = temp_project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{temp_project_dir.name}-prd.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## 2. 功能范围",
                "",
                "### 用户登录",
                "- 支持邮箱密码登录",
                "",
                "### Canvas 工作台",
                "- 提供交互式画布编辑",
            ]
        ),
        encoding="utf-8",
    )
    (output_dir / f"{temp_project_dir.name}-research.md").write_text(
        "| 优先级 | 事项 | 工作量 |\n|:---:|:---|:---|\n| P0 | Canvas 工作台 | 大 |\n",
        encoding="utf-8",
    )
    change_dir = temp_project_dir / ".super-dev" / "changes" / "release-hardening-finalization"
    (change_dir / "tasks.md").write_text(
        "# Tasks\n\n- [x] 用户登录\n- [ ] Canvas 工作台\n",
        encoding="utf-8",
    )

    evaluator = ReleaseReadinessEvaluator(temp_project_dir)
    report = evaluator.evaluate(verify_tests=False)

    scope_check = next(check for check in report.checks if check.name == "Scope Coverage")
    assert scope_check.passed is False
    assert "high_priority_gaps=1" in scope_check.detail
