"""
Super Dev Web API 集成测试
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import super_dev.web.api as web_api
from super_dev.orchestrator import Phase, PhaseResult


@pytest.fixture(autouse=True)
def clear_run_store():
    web_api._RUN_STORE.clear()
    yield
    web_api._RUN_STORE.clear()


class TestWebAPI:
    def test_health_endpoint(self):
        client = TestClient(web_api.app)
        resp = client.get("/api/health")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "healthy"

    def test_init_and_get_config(self, temp_project_dir: Path):
        client = TestClient(web_api.app)

        init_resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={
                "name": "api-demo",
                "description": "api demo project",
                "platform": "web",
                "frontend": "react",
                "backend": "node",
                "domain": "auth",
            },
        )
        assert init_resp.status_code == 200

        config_resp = client.get(
            "/api/config",
            params={"project_dir": str(temp_project_dir)},
        )
        assert config_resp.status_code == 200
        payload = config_resp.json()
        assert payload["name"] == "api-demo"
        assert payload["frontend"] == "react"
        assert payload["language_preferences"] == []
        assert payload["host_compatibility_min_score"] == 80
        assert payload["host_compatibility_min_ready_hosts"] == 1

    def test_policy_get_and_update(self, temp_project_dir: Path):
        client = TestClient(web_api.app)

        preset_resp = client.get("/api/policy/presets")
        assert preset_resp.status_code == 200
        preset_ids = {item["id"] for item in preset_resp.json()["presets"]}
        assert {"default", "balanced", "enterprise"}.issubset(preset_ids)

        get_resp = client.get(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
        )
        assert get_resp.status_code == 200
        default_payload = get_resp.json()
        assert default_payload["require_redteam"] is True
        assert default_payload["require_quality_gate"] is True
        assert default_payload["min_quality_threshold"] == 80
        assert default_payload["enforce_required_hosts_ready"] is False
        assert default_payload["min_required_host_score"] == 80
        assert default_payload["policy_exists"] is False

        update_resp = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={
                "preset": "enterprise",
                "min_quality_threshold": 88,
                "allowed_cicd_platforms": ["github", "gitlab"],
                "required_hosts": ["codex-cli", "claude-code"],
                "enforce_required_hosts_ready": True,
                "min_required_host_score": 86,
            },
        )
        assert update_resp.status_code == 200
        updated_payload = update_resp.json()
        assert updated_payload["min_quality_threshold"] == 88
        assert updated_payload["allowed_cicd_platforms"] == ["github", "gitlab"]
        assert updated_payload["require_host_profile"] is True
        assert set(updated_payload["required_hosts"]) == {"codex-cli", "claude-code"}
        assert updated_payload["enforce_required_hosts_ready"] is True
        assert updated_payload["min_required_host_score"] == 86
        assert updated_payload["policy_exists"] is True

        policy_path = temp_project_dir / ".super-dev" / "policy.yaml"
        assert policy_path.exists()

        get_after_resp = client.get(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
        )
        assert get_after_resp.status_code == 200
        get_after_payload = get_after_resp.json()
        assert get_after_payload["min_quality_threshold"] == 88
        assert set(get_after_payload["required_hosts"]) == {"codex-cli", "claude-code"}

    def test_policy_update_rejects_invalid_values(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        invalid_threshold = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={"min_quality_threshold": 101},
        )
        assert invalid_threshold.status_code == 400

        invalid_cicd = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={"allowed_cicd_platforms": ["github", "unknown"]},
        )
        assert invalid_cicd.status_code == 400

        invalid_host = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={"required_hosts": ["codex-cli", "not-a-host"]},
        )
        assert invalid_host.status_code == 400

        invalid_required_score = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={"min_required_host_score": 101},
        )
        assert invalid_required_score.status_code == 400

        invalid_preset = client.put(
            "/api/policy",
            params={"project_dir": str(temp_project_dir)},
            json={"preset": "not-exists"},
        )
        assert invalid_preset.status_code == 400

    def test_workflow_run_and_status(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)

        init_resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={"name": "api-workflow", "platform": "web", "frontend": "react", "backend": "node"},
        )
        assert init_resp.status_code == 200

        async def fake_run(self, phases=None, context=None, **kwargs):
            return {
                Phase.DISCOVERY: PhaseResult(
                    phase=Phase.DISCOVERY,
                    success=True,
                    duration=0.01,
                    quality_score=90.0,
                )
            }

        monkeypatch.setattr(web_api.WorkflowEngine, "run", fake_run)

        run_resp = client.post(
            "/api/workflow/run",
            params={"project_dir": str(temp_project_dir)},
            json={"phases": ["discovery"]},
        )
        assert run_resp.status_code == 200
        run_payload = run_resp.json()
        assert run_payload["status"] == "started"
        run_id = run_payload["run_id"]
        assert run_id

        status_resp = client.get(
            f"/api/workflow/status/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert status_resp.status_code == 200
        status_payload = status_resp.json()
        assert status_payload["run_id"] == run_id
        assert status_payload["status"] in {"completed", "failed", "running", "queued", "cancelling", "cancelled"}
        assert "progress" in status_payload

        # 持久化文件存在
        persisted = temp_project_dir / ".super-dev" / "runs" / f"{run_id}.json"
        assert persisted.exists()

        # 模拟进程重启后仍可从磁盘读取
        web_api._RUN_STORE.clear()
        status_resp_2 = client.get(
            f"/api/workflow/status/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert status_resp_2.status_code == 200
        assert status_resp_2.json()["run_id"] == run_id

    def test_workflow_run_passes_request_context(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)

        init_resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={
                "name": "api-context",
                "description": "from-init",
                "platform": "web",
                "frontend": "react",
                "backend": "node",
            },
        )
        assert init_resp.status_code == 200

        observed: dict[str, str] = {}

        async def fake_run(self, phases=None, context=None, **kwargs):
            assert context is not None
            observed["name"] = context.user_input.get("name")
            observed["description"] = context.user_input.get("description")
            observed["platform"] = context.user_input.get("platform")
            observed["frontend"] = context.user_input.get("frontend")
            observed["backend"] = context.user_input.get("backend")
            observed["domain"] = context.user_input.get("domain")
            observed["language_preferences"] = context.user_input.get("language_preferences")
            observed["cicd"] = context.user_input.get("cicd")
            return {
                Phase.DISCOVERY: PhaseResult(
                    phase=Phase.DISCOVERY,
                    success=True,
                    duration=0.01,
                    quality_score=90.0,
                )
            }

        monkeypatch.setattr(web_api.WorkflowEngine, "run", fake_run)

        run_resp = client.post(
            "/api/workflow/run",
            params={"project_dir": str(temp_project_dir)},
            json={
                "phases": ["discovery"],
                "name": "override-name",
                "description": "override-desc",
                "platform": "mobile",
                "frontend": "vue",
                "backend": "python",
                "domain": "medical",
                "language_preferences": ["python", "typescript", "rust"],
                "cicd": "gitlab",
            },
        )
        assert run_resp.status_code == 200
        assert observed == {
            "name": "override-name",
            "description": "override-desc",
            "platform": "mobile",
            "frontend": "vue",
            "backend": "python",
            "domain": "medical",
            "language_preferences": ["python", "typescript", "rust"],
            "cicd": "gitlab",
        }

    def test_workflow_status_includes_redteam_output(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)

        init_resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={"name": "api-redteam", "platform": "web", "frontend": "react", "backend": "python"},
        )
        assert init_resp.status_code == 200

        async def fake_run(self, phases=None, context=None, **kwargs):
            return {
                Phase.REDTEAM: PhaseResult(
                    phase=Phase.REDTEAM,
                    success=True,
                    duration=0.02,
                    quality_score=86.0,
                    output={
                        "status": "redteam_complete",
                        "score": 86,
                        "critical_count": 0,
                        "high_count": 1,
                        "issues": {
                            "security": [
                                {
                                    "severity": "high",
                                    "category": "命令执行",
                                    "description": "检测到高风险代码模式: app.py:12",
                                    "recommendation": "避免 shell=True",
                                    "file_path": str(temp_project_dir / "app.py"),
                                    "line": 12,
                                }
                            ]
                        },
                    },
                )
            }

        monkeypatch.setattr(web_api.WorkflowEngine, "run", fake_run)

        run_resp = client.post(
            "/api/workflow/run",
            params={"project_dir": str(temp_project_dir)},
            json={"phases": ["redteam"]},
        )
        assert run_resp.status_code == 200
        run_id = run_resp.json()["run_id"]

        status_resp = client.get(
            f"/api/workflow/status/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert status_resp.status_code == 200
        payload = status_resp.json()
        assert payload["status"] in {"completed", "failed", "running", "queued", "cancelling", "cancelled"}
        assert payload["results"]
        redteam_result = payload["results"][0]
        assert redteam_result["phase"] == "redteam"
        assert redteam_result["output"]["issues"]["security"][0]["line"] == 12

    def test_workflow_run_invalid_phase(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={"name": "api-invalid-phase", "platform": "web", "frontend": "react", "backend": "node"},
        )

        run_resp = client.post(
            "/api/workflow/run",
            params={"project_dir": str(temp_project_dir)},
            json={"phases": ["not-a-phase"]},
        )
        assert run_resp.status_code == 400

    def test_init_rejects_invalid_host_compatibility_threshold(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={
                "name": "api-invalid-threshold",
                "platform": "web",
                "frontend": "react",
                "backend": "node",
                "host_compatibility_min_score": 120,
            },
        )
        assert resp.status_code == 400

    def test_workflow_status_not_found(self):
        client = TestClient(web_api.app)
        status_resp = client.get("/api/workflow/status/does-not-exist")
        assert status_resp.status_code == 404

    def test_workflow_runs_history(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)

        init_resp = client.post(
            "/api/init",
            params={"project_dir": str(temp_project_dir)},
            json={"name": "api-history", "platform": "web", "frontend": "react", "backend": "node"},
        )
        assert init_resp.status_code == 200

        async def fake_run(self, phases=None, context=None, **kwargs):
            return {
                Phase.DISCOVERY: PhaseResult(
                    phase=Phase.DISCOVERY,
                    success=True,
                    duration=0.01,
                    quality_score=90.0,
                )
            }

        monkeypatch.setattr(web_api.WorkflowEngine, "run", fake_run)

        run_resp = client.post(
            "/api/workflow/run",
            params={"project_dir": str(temp_project_dir)},
            json={"phases": ["discovery"]},
        )
        assert run_resp.status_code == 200

        history_resp = client.get(
            "/api/workflow/runs",
            params={"project_dir": str(temp_project_dir), "limit": 10},
        )
        assert history_resp.status_code == 200
        payload = history_resp.json()
        assert payload["count"] >= 1
        assert isinstance(payload["runs"], list)

        bad_limit_resp = client.get(
            "/api/workflow/runs",
            params={"project_dir": str(temp_project_dir), "limit": 0},
        )
        assert bad_limit_resp.status_code == 400

    def test_workflow_artifacts_list_and_archive(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        run_id = "artifact001"
        web_api._store_run_state(
            run_id,
            persist_dir=temp_project_dir,
            status="completed",
            project_dir=str(temp_project_dir),
            requested_phases=["discovery", "deployment"],
            completed_phases=["discovery", "deployment"],
            progress=100,
            message="完成",
            cancel_requested=False,
            started_at=web_api._utc_now(),
            finished_at=web_api._utc_now(),
            results=[],
        )

        output_dir = temp_project_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "demo-prd.md").write_text("# demo", encoding="utf-8")
        (temp_project_dir / ".env.deploy.example").write_text("FOO=bar", encoding="utf-8")

        list_resp = client.get(
            f"/api/workflow/artifacts/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert list_resp.status_code == 200
        payload = list_resp.json()
        assert payload["run_id"] == run_id
        assert payload["count"] >= 2
        relative_paths = {item["relative_path"] for item in payload["items"]}
        assert "output/demo-prd.md" in relative_paths
        assert ".env.deploy.example" in relative_paths

        archive_resp = client.get(
            f"/api/workflow/artifacts/{run_id}/archive",
            params={"project_dir": str(temp_project_dir)},
        )
        assert archive_resp.status_code == 200
        assert archive_resp.headers.get("content-type", "").startswith("application/zip")
        disposition = archive_resp.headers.get("content-disposition", "")
        assert f"workflow-{run_id}-artifacts.zip" in disposition
        assert len(archive_resp.content) > 0

    def test_workflow_artifacts_not_found(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        list_resp = client.get(
            "/api/workflow/artifacts/not-exists",
            params={"project_dir": str(temp_project_dir)},
        )
        assert list_resp.status_code == 404

        archive_resp = client.get(
            "/api/workflow/artifacts/not-exists/archive",
            params={"project_dir": str(temp_project_dir)},
        )
        assert archive_resp.status_code == 404

    def test_workflow_cancel_not_found(self):
        client = TestClient(web_api.app)
        cancel_resp = client.post("/api/workflow/cancel/does-not-exist")
        assert cancel_resp.status_code == 404

    def test_workflow_cancel_queued(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        run_id = "queued001"
        web_api._store_run_state(
            run_id,
            persist_dir=temp_project_dir,
            status="queued",
            project_dir=str(temp_project_dir),
            requested_phases=["discovery"],
            completed_phases=[],
            progress=0,
            message="工作流排队中",
            cancel_requested=False,
            started_at=web_api._utc_now(),
            finished_at=None,
            results=[],
        )

        cancel_resp = client.post(
            f"/api/workflow/cancel/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert cancel_resp.status_code == 200
        payload = cancel_resp.json()
        assert payload["status"] == "cancelled"

        status_resp = client.get(
            f"/api/workflow/status/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "cancelled"

    def test_workflow_cancel_running(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        run_id = "running001"
        web_api._store_run_state(
            run_id,
            persist_dir=temp_project_dir,
            status="running",
            project_dir=str(temp_project_dir),
            requested_phases=["discovery", "qa"],
            completed_phases=["discovery"],
            progress=50,
            message="工作流运行中",
            cancel_requested=False,
            started_at=web_api._utc_now(),
            finished_at=None,
            results=[],
        )

        cancel_resp = client.post(
            f"/api/workflow/cancel/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert cancel_resp.status_code == 200
        payload = cancel_resp.json()
        assert payload["status"] == "cancelling"

        status_resp = client.get(
            f"/api/workflow/status/{run_id}",
            params={"project_dir": str(temp_project_dir)},
        )
        assert status_resp.status_code == 200
        status_payload = status_resp.json()
        assert status_payload["status"] == "cancelling"
        assert status_payload["cancel_requested"] is True

    def test_expert_advice_generation(self, temp_project_dir: Path):
        client = TestClient(web_api.app)

        experts_resp = client.get("/api/experts")
        assert experts_resp.status_code == 200
        expert_ids = {item["id"] for item in experts_resp.json()["experts"]}
        assert "PM" in expert_ids
        assert "RCA" in expert_ids

        advice_resp = client.post(
            "/api/experts/pm/advice",
            params={"project_dir": str(temp_project_dir)},
            json={"prompt": "请帮我规划登录功能"},
        )
        assert advice_resp.status_code == 200
        payload = advice_resp.json()
        assert payload["expert_id"] == "PM"
        assert "建议清单" in payload["content"]
        assert Path(payload["file_path"]).exists()

    def test_expert_advice_unknown_expert(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        advice_resp = client.post(
            "/api/experts/unknown/advice",
            params={"project_dir": str(temp_project_dir)},
            json={"prompt": "test"},
        )
        assert advice_resp.status_code == 404

    def test_expert_advice_history_and_content(self, temp_project_dir: Path):
        client = TestClient(web_api.app)

        # 先生成两份建议
        r1 = client.post(
            "/api/experts/pm/advice",
            params={"project_dir": str(temp_project_dir)},
            json={"prompt": "规划用户增长"},
        )
        assert r1.status_code == 200
        f1 = r1.json()["file_name"]

        r2 = client.post(
            "/api/experts/qa/advice",
            params={"project_dir": str(temp_project_dir)},
            json={"prompt": "建立测试策略"},
        )
        assert r2.status_code == 200
        f2 = r2.json()["file_name"]

        history_resp = client.get(
            "/api/experts/advice/history",
            params={"project_dir": str(temp_project_dir), "limit": 10},
        )
        assert history_resp.status_code == 200
        payload = history_resp.json()
        assert payload["count"] >= 2
        assert any(item["file_name"] == f1 for item in payload["items"])
        assert any(item["file_name"] == f2 for item in payload["items"])

        content_resp = client.get(
            "/api/experts/advice/content",
            params={"project_dir": str(temp_project_dir), "file_name": f1},
        )
        assert content_resp.status_code == 200
        assert "PM 专家建议" in content_resp.json()["content"]

        bad_name_resp = client.get(
            "/api/experts/advice/content",
            params={"project_dir": str(temp_project_dir), "file_name": "../x.md"},
        )
        assert bad_name_resp.status_code == 400

        missing_resp = client.get(
            "/api/experts/advice/content",
            params={"project_dir": str(temp_project_dir), "file_name": "expert-none-advice.md"},
        )
        assert missing_resp.status_code == 404

    def test_deploy_platforms(self):
        client = TestClient(web_api.app)
        resp = client.get("/api/deploy/platforms")
        assert resp.status_code == 200
        payload = resp.json()
        ids = {item["id"] for item in payload["platforms"]}
        assert {"all", "github", "gitlab", "jenkins", "azure", "bitbucket"}.issubset(ids)

    def test_catalogs_endpoint(self):
        client = TestClient(web_api.app)
        resp = client.get("/api/catalogs")
        assert resp.status_code == 200
        payload = resp.json()

        platform_ids = {item["id"] for item in payload["platforms"]}
        assert {"web", "mobile", "wechat", "desktop"}.issubset(platform_ids)

        frontend_ids = {item["id"] for item in payload["frontends"]}
        assert {"react", "vue", "angular", "svelte", "none"}.issubset(frontend_ids)

        backend_ids = {item["id"] for item in payload["backends"]}
        assert {"node", "python", "rust", "csharp", "dart", "none"}.issubset(backend_ids)

        domain_ids = {item["id"] for item in payload["domains"]}
        assert {"", "fintech", "auth", "content", "saas"}.issubset(domain_ids)

        cicd_platform_ids = {item["id"] for item in payload["cicd_platforms"]}
        assert {"all", "github", "gitlab", "jenkins", "azure", "bitbucket"}.issubset(cicd_platform_ids)

        host_tool_ids = {item["id"] for item in payload["host_tools"]}
        assert {
            "claude-code",
            "codebuddy-cli",
            "codebuddy",
            "codex-cli",
            "cursor-cli",
            "windsurf",
            "gemini-cli",
            "iflow",
            "kimi-cli",
            "kiro-cli",
            "opencode",
            "qoder-cli",
            "cursor",
            "kiro",
            "qoder",
            "trae",
        }.issubset(host_tool_ids)
        claude_host = next(item for item in payload["host_tools"] if item["id"] == "claude-code")
        assert claude_host["category"] == "cli"
        assert ".claude/CLAUDE.md" in claude_host["integration_files"]
        assert claude_host["slash_command_file"] == ".claude/commands/super-dev.md"
        assert claude_host["commands"]["setup"].startswith("super-dev setup --host claude-code")

        language_ids = {item["id"] for item in payload["languages"]}
        assert {"python", "typescript", "rust", "sql", "assembly"}.issubset(language_ids)

    def test_hosts_doctor_endpoint(self, temp_project_dir: Path, monkeypatch):
        fake_home = temp_project_dir / "fake-home"
        fake_home.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("HOME", str(fake_home))

        client = TestClient(web_api.app)
        resp = client.get(
            "/api/hosts/doctor",
            params={
                "project_dir": str(temp_project_dir),
                "host": "claude-code",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["selected_targets"] == ["claude-code"]
        assert "report" in payload
        assert "compatibility" in payload
        host = payload["report"]["hosts"]["claude-code"]
        assert host["ready"] is False
        assert {"integrate", "skill", "slash"}.issubset(set(host["missing"]))

    def test_hosts_doctor_skill_only_host_skips_slash(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.get(
            "/api/hosts/doctor",
            params={
                "project_dir": str(temp_project_dir),
                "host": "trae",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        host = payload["report"]["hosts"]["trae"]
        assert host["ready"] is False
        assert "slash" not in host["missing"]
        assert host["checks"]["slash"]["ok"] is True
        assert host["checks"]["slash"]["mode"] == "skill-only"

    def test_hosts_doctor_endpoint_ready_after_files_present(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        (temp_project_dir / ".claude" / "CLAUDE.md").parent.mkdir(parents=True, exist_ok=True)
        (temp_project_dir / ".claude" / "CLAUDE.md").write_text("ok", encoding="utf-8")
        (temp_project_dir / ".claude" / "commands").mkdir(parents=True, exist_ok=True)
        (temp_project_dir / ".claude" / "commands" / "super-dev.md").write_text("ok", encoding="utf-8")
        (temp_project_dir / ".claude" / "skills" / "super-dev-core").mkdir(parents=True, exist_ok=True)
        (temp_project_dir / ".claude" / "skills" / "super-dev-core" / "SKILL.md").write_text(
            "# skill",
            encoding="utf-8",
        )

        resp = client.get(
            "/api/hosts/doctor",
            params={
                "project_dir": str(temp_project_dir),
                "host": "claude-code",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["report"]["hosts"]["claude-code"]["ready"] is True
        assert payload["compatibility"]["hosts"]["claude-code"]["score"] == 100.0

    def test_deploy_precheck_github(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)
        monkeypatch.setenv("DOCKER_USERNAME", "demo-user")
        (temp_project_dir / "Dockerfile").write_text("FROM node:18", encoding="utf-8")

        resp = client.get(
            "/api/deploy/precheck",
            params={
                "project_dir": str(temp_project_dir),
                "cicd_platform": "github",
                "include_runtime": True,
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["cicd_platform"] == "github"
        assert payload["target_count"] >= 10
        assert "Dockerfile" in payload["existing_files"]
        checks = {item["name"]: item for item in payload["env_checks"]}
        assert checks["DOCKER_USERNAME"]["present"] is True
        assert checks["DOCKER_PASSWORD"]["present"] is False
        assert "DOCKER_PASSWORD" in payload["missing_env"]

    def test_deploy_precheck_invalid_platform(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.get(
            "/api/deploy/precheck",
            params={"project_dir": str(temp_project_dir), "cicd_platform": "invalid"},
        )
        assert resp.status_code == 400

    def test_deploy_remediation_only_missing(self, monkeypatch):
        client = TestClient(web_api.app)
        monkeypatch.setenv("DOCKER_USERNAME", "demo-user")

        resp = client.get(
            "/api/deploy/remediation",
            params={"cicd_platform": "github", "only_missing": True},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["cicd_platform"] == "github"

        item_names = {item["name"] for item in payload["items"]}
        assert "DOCKER_PASSWORD" in item_names
        assert "DOCKER_USERNAME" not in item_names
        assert len(payload["platform_guidance"]) >= 1

    def test_deploy_remediation_include_present(self, monkeypatch):
        client = TestClient(web_api.app)
        monkeypatch.setenv("DOCKER_USERNAME", "demo-user")

        resp = client.get(
            "/api/deploy/remediation",
            params={"cicd_platform": "github", "only_missing": False},
        )
        assert resp.status_code == 200
        payload = resp.json()
        item_map = {item["name"]: item for item in payload["items"]}
        assert "DOCKER_USERNAME" in item_map
        assert item_map["DOCKER_USERNAME"]["present"] is True

    def test_deploy_remediation_invalid_platform(self):
        client = TestClient(web_api.app)
        resp = client.get(
            "/api/deploy/remediation",
            params={"cicd_platform": "invalid"},
        )
        assert resp.status_code == 400

    def test_deploy_remediation_export(self, temp_project_dir: Path, monkeypatch):
        client = TestClient(web_api.app)
        monkeypatch.setenv("DOCKER_USERNAME", "demo-user")

        resp = client.post(
            "/api/deploy/remediation/export",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "github",
                "only_missing": True,
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["cicd_platform"] == "github"
        assert payload["split_by_platform"] is True
        assert isinstance(payload["generated_files"], list)
        generated_names = {Path(p).name for p in payload["generated_files"]}
        assert ".env.deploy.example" in generated_names

        env_path = Path(payload["env_file"]["path"])
        checklist_path = Path(payload["checklist_file"]["path"])
        assert env_path.exists()
        assert checklist_path.exists()

        env_content = env_path.read_text(encoding="utf-8")
        assert "DOCKER_PASSWORD" in env_content
        assert "DOCKER_USERNAME" not in env_content

        checklist_content = checklist_path.read_text(encoding="utf-8")
        assert "Deploy Remediation Checklist" in checklist_content
        assert "Platform Guidance" in checklist_content

    def test_deploy_remediation_export_all_with_split(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/deploy/remediation/export",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "all",
                "only_missing": True,
                "split_by_platform": True,
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["cicd_platform"] == "all"
        assert payload["split_by_platform"] is True
        assert len(payload["per_platform_files"]) == 5

        per_platform = {item["platform"] for item in payload["per_platform_files"]}
        assert per_platform == {"github", "gitlab", "jenkins", "azure", "bitbucket"}
        for item in payload["per_platform_files"]:
            assert Path(item["env_file"]["path"]).exists()
            assert Path(item["checklist_file"]["path"]).exists()

    def test_deploy_remediation_export_invalid_file_name(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/deploy/remediation/export",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "github",
                "env_file_name": "bad/name.env",
            },
        )
        assert resp.status_code == 400

    def test_deploy_remediation_archive_download(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.get(
            "/api/deploy/remediation/archive",
            params={
                "project_dir": str(temp_project_dir),
                "cicd_platform": "all",
                "only_missing": True,
                "split_by_platform": True,
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("application/zip")
        disposition = resp.headers.get("content-disposition", "")
        assert "deploy-remediation-all.zip" in disposition
        assert len(resp.content) > 0

    def test_deploy_generate_all_platforms(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/deploy/generate",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "all",
                "include_runtime": True,
                "overwrite": True,
                "name": "demo-app",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["status"] == "success"
        assert payload["generated_count"] >= 6
        assert ".github/workflows/ci.yml" in payload["generated_files"]
        assert ".gitlab-ci.yml" in payload["generated_files"]
        assert "Jenkinsfile" in payload["generated_files"]
        assert ".azure-pipelines.yml" in payload["generated_files"]
        assert "bitbucket-pipelines.yml" in payload["generated_files"]
        assert "Dockerfile" in payload["generated_files"]
        assert "k8s/deployment.yaml" in payload["generated_files"]

    def test_deploy_generate_cicd_only(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/deploy/generate",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "github",
                "include_runtime": False,
                "overwrite": True,
                "name": "demo-app",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "Dockerfile" not in payload["generated_files"]
        assert "k8s/deployment.yaml" not in payload["generated_files"]
        assert ".github/workflows/ci.yml" in payload["generated_files"]
        assert ".github/workflows/cd.yml" in payload["generated_files"]

    def test_deploy_generate_invalid_platform(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        resp = client.post(
            "/api/deploy/generate",
            params={"project_dir": str(temp_project_dir)},
            json={"cicd_platform": "invalid-platform"},
        )
        assert resp.status_code == 400

    def test_deploy_generate_without_overwrite(self, temp_project_dir: Path):
        client = TestClient(web_api.app)
        existing = temp_project_dir / ".gitlab-ci.yml"
        existing.write_text("old-content", encoding="utf-8")

        resp = client.post(
            "/api/deploy/generate",
            params={"project_dir": str(temp_project_dir)},
            json={
                "cicd_platform": "gitlab",
                "include_runtime": False,
                "overwrite": False,
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert ".gitlab-ci.yml" in payload["skipped_files"]
        assert payload["skipped_count"] == 1
        assert existing.read_text(encoding="utf-8") == "old-content"
