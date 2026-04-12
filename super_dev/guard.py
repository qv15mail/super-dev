"""Real-time governance guard that watches file changes and validates them."""

import logging
import re
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("super_dev.guard")


class GovernanceGuard:
    """Watches project files and validates changes against governance rules."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.config_dir = project_dir / ".super-dev"
        self.output_dir = project_dir / "output"
        self.violations: list[dict[str, Any]] = []
        self._last_check: dict[str, float] = {}

    def check_file(self, file_path: Path) -> list[str]:
        """Validate a single file against governance rules."""
        issues: list[str] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return issues

        # Rule 1: No emoji icons in code files
        if file_path.suffix in (".tsx", ".ts", ".jsx", ".js"):
            emoji_pattern = re.compile(
                "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
                "\U0001f1e0-\U0001f1ff\U00002702-\U000027b0\U000024c2-\U0001f251]"
            )
            for i, line in enumerate(content.split("\n"), 1):
                if emoji_pattern.search(line):
                    issues.append(f"{file_path}:{i} — emoji detected in code")

        # Rule 2: No hardcoded color values in frontend
        if file_path.suffix in (".tsx", ".css"):
            hex_colors = re.findall(r"#[0-9a-fA-F]{3,8}\b", content)
            if hex_colors and "theme" not in content.lower() and "token" not in content.lower():
                issues.append(
                    f"{file_path} — hardcoded colors without theme tokens: {hex_colors[:3]}"
                )

        # Rule 3: No console.log in production code
        if file_path.suffix in (".ts", ".tsx", ".js", ".jsx"):
            for i, line in enumerate(content.split("\n"), 1):
                if "console.log" in line and "// debug" not in line.lower():
                    issues.append(f"{file_path}:{i} — console.log in production code")

        return issues

    def run(self, watch: bool = True, interval: float = 2.0) -> int:
        """Run the guard. Returns number of violations found."""
        from .terminal import create_console

        console = create_console()

        console.print(
            "[bold cyan]Super Dev Guard[/bold cyan] — watching for governance violations"
        )
        console.print(f"Project: {self.project_dir}")
        console.print("")

        total_violations = 0

        while True:
            # Scan all tracked files
            for ext in ("*.tsx", "*.ts", "*.jsx", "*.js", "*.py"):
                for file_path in self.project_dir.rglob(ext):
                    # Skip node_modules, .next, etc.
                    parts = file_path.parts
                    if any(
                        p in parts
                        for p in (
                            "node_modules",
                            ".next",
                            "dist",
                            "__pycache__",
                            ".super-dev",
                        )
                    ):
                        continue

                    mtime = file_path.stat().st_mtime
                    key = str(file_path)
                    if key in self._last_check and mtime <= self._last_check[key]:
                        continue
                    self._last_check[key] = mtime

                    issues = self.check_file(file_path)
                    for issue in issues:
                        total_violations += 1
                        self.violations.append({"file": str(file_path), "issue": issue})
                        console.print(f"[red]VIOLATION[/red] {issue}")

            if not watch:
                break

            time.sleep(interval)

        if total_violations == 0:
            console.print("[green]All checks passed[/green]")
        else:
            console.print(f"[yellow]Found {total_violations} violation(s)[/yellow]")

        return total_violations
