# -*- coding: utf-8 -*-
"""
红队审查器测试
"""

from pathlib import Path

from super_dev.reviewers.redteam import RedTeamReviewer


class TestRedTeamReviewer:
    def test_detects_hardcoded_secret_and_shell_true(self, temp_project_dir: Path):
        src_dir = temp_project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "app.py").write_text(
            """
import subprocess

API_KEY = "sk_live_real_secret_123456"

def run_cmd(user_input: str):
    return subprocess.run(f"echo {user_input}", shell=True)
""",
            encoding="utf-8",
        )

        reviewer = RedTeamReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "python", "frontend": "none"},
        )
        report = reviewer.review()

        categories = {i.category for i in report.security_issues}
        assert "硬编码凭据" in categories
        assert "命令执行" in categories
        assert any("app.py:" in i.description for i in report.security_issues)

    def test_ignores_placeholder_secrets(self, temp_project_dir: Path):
        src_dir = temp_project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "config.py").write_text(
            """
API_KEY = "your-api-key"
PASSWORD = "placeholder"
""",
            encoding="utf-8",
        )

        reviewer = RedTeamReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "none", "frontend": "none"},
        )
        report = reviewer.review()

        assert not any(i.category == "硬编码凭据" for i in report.security_issues)

    def test_detects_async_requests_and_n_plus_one(self, temp_project_dir: Path):
        src_dir = temp_project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "perf.py").write_text(
            """
import requests

async def fetch_data():
    return requests.get("https://example.com/api")

def load_users(users, db):
    for user in users:
        db.query("select * from orders where user_id=" + str(user.id))
""",
            encoding="utf-8",
        )

        reviewer = RedTeamReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "python", "frontend": "none"},
        )
        report = reviewer.review()

        assert any(
            i.category == "API" and "perf.py:" in i.description
            for i in report.performance_issues
        )
        assert any(
            i.category == "数据库" and "perf.py:" in i.description
            for i in report.performance_issues
        )

    def test_architecture_flags_missing_tests_ci_and_large_file(self, temp_project_dir: Path):
        src_dir = temp_project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "huge.py").write_text(
            "\n".join(["print('x')"] * 2105),
            encoding="utf-8",
        )

        reviewer = RedTeamReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "python", "frontend": "none"},
        )
        report = reviewer.review()

        assert any("tests 目录" in i.description for i in report.architecture_issues)
        assert any("CI/CD" in i.description for i in report.architecture_issues)
        assert any("超大单体文件" in i.description for i in report.architecture_issues)

    def test_fallback_scan_project_root_files(self, temp_project_dir: Path):
        (temp_project_dir / "main.py").write_text(
            'token = "real_token_abcdef123456"\n',
            encoding="utf-8",
        )

        reviewer = RedTeamReviewer(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "none", "frontend": "none"},
        )
        report = reviewer.review()

        assert any(i.category == "硬编码凭据" for i in report.security_issues)
