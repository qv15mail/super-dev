"""
项目交付打包器

在流水线最后阶段收敛产物，输出交付清单、报告和压缩包。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass(frozen=True)
class ArtifactSpec:
    """交付物规则定义"""

    path: Path
    required: bool
    reason: str


class DeliveryPackager:
    """交付包生成器"""

    def __init__(self, project_dir: Path, name: str, version: str = "2.0.0"):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.version = version

    def package(self, cicd_platform: str = "all") -> dict[str, object]:
        """生成交付清单、报告和压缩包"""
        output_dir = self.project_dir / "output" / "delivery"
        output_dir.mkdir(parents=True, exist_ok=True)

        specs = self._artifact_specs(cicd_platform=cicd_platform)
        included_files: list[str] = []
        missing_required: list[dict[str, str]] = []

        for spec in specs:
            if spec.path.exists():
                included_files.append(self._relative(spec.path))
            elif spec.required:
                missing_required.append(
                    {
                        "path": self._relative(spec.path),
                        "reason": spec.reason,
                    }
                )

        migration_files = self._collect_migration_files()
        if migration_files:
            included_files.extend(self._relative(path) for path in migration_files)
        else:
            missing_required.append(
                {
                    "path": "migrations/*",
                    "reason": "缺少数据库迁移脚本（至少应生成一种 ORM 迁移文件）",
                }
            )

        included_files = sorted(set(included_files))
        status = "ready" if not missing_required else "incomplete"

        manifest: dict[str, object] = {
            "project_name": self.name,
            "version": self.version,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "status": status,
            "cicd_platform": cicd_platform,
            "included_files": included_files,
            "missing_required": missing_required,
            "summary": {
                "included_count": len(included_files),
                "missing_required_count": len(missing_required),
            },
        }

        manifest_file = output_dir / f"{self.name}-delivery-manifest.json"
        manifest_file.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        report_file = output_dir / f"{self.name}-delivery-report.md"
        report_file.write_text(self._to_markdown(manifest), encoding="utf-8")

        archive_file = output_dir / f"{self.name}-delivery-v{self.version}.zip"
        self._build_archive(
            archive_path=archive_file,
            included_files=included_files,
            extra_files=[manifest_file, report_file],
        )

        return {
            "status": status,
            "manifest_file": str(manifest_file),
            "report_file": str(report_file),
            "archive_file": str(archive_file),
            "included_count": len(included_files),
            "missing_required_count": len(missing_required),
            "missing_required": missing_required,
        }

    def _artifact_specs(self, cicd_platform: str) -> list[ArtifactSpec]:
        output_dir = self.project_dir / "output"
        specs = [
            ArtifactSpec(output_dir / f"{self.name}-research.md", True, "缺少需求增强报告"),
            ArtifactSpec(output_dir / f"{self.name}-prd.md", True, "缺少 PRD"),
            ArtifactSpec(output_dir / f"{self.name}-architecture.md", True, "缺少架构文档"),
            ArtifactSpec(output_dir / f"{self.name}-uiux.md", True, "缺少 UI/UX 文档"),
            ArtifactSpec(output_dir / f"{self.name}-execution-plan.md", True, "缺少执行路线图"),
            ArtifactSpec(output_dir / f"{self.name}-frontend-blueprint.md", True, "缺少前端蓝图"),
            ArtifactSpec(output_dir / f"{self.name}-redteam.md", True, "缺少红队报告"),
            ArtifactSpec(output_dir / f"{self.name}-quality-gate.md", True, "缺少质量门禁报告"),
            ArtifactSpec(output_dir / f"{self.name}-code-review.md", True, "缺少代码审查指南"),
            ArtifactSpec(output_dir / f"{self.name}-ai-prompt.md", True, "缺少 AI 提示词"),
            ArtifactSpec(output_dir / "frontend" / "index.html", True, "缺少前端演示页面"),
            ArtifactSpec(output_dir / "frontend" / "styles.css", True, "缺少前端演示样式"),
            ArtifactSpec(output_dir / "frontend" / "app.js", True, "缺少前端演示脚本"),
            ArtifactSpec(self.project_dir / "backend" / "API_CONTRACT.md", True, "缺少 API 契约"),
            ArtifactSpec(self.project_dir / ".env.deploy.example", True, "缺少部署环境模板"),
            ArtifactSpec(
                self.project_dir / "output" / "deploy" / "all-secrets-checklist.md",
                True,
                "缺少部署 Secrets 检查清单",
            ),
        ]
        specs.extend(self._cicd_specs(cicd_platform=cicd_platform))
        return specs

    def _cicd_specs(self, cicd_platform: str) -> list[ArtifactSpec]:
        mapping: dict[str, list[str]] = {
            "github": [".github/workflows/ci.yml", ".github/workflows/cd.yml"],
            "gitlab": [".gitlab-ci.yml"],
            "jenkins": ["Jenkinsfile"],
            "azure": [".azure-pipelines.yml"],
            "bitbucket": ["bitbucket-pipelines.yml"],
            "all": [
                ".github/workflows/ci.yml",
                ".github/workflows/cd.yml",
                ".gitlab-ci.yml",
                "Jenkinsfile",
                ".azure-pipelines.yml",
                "bitbucket-pipelines.yml",
            ],
        }
        files = mapping.get(cicd_platform, mapping["github"])
        return [
            ArtifactSpec(self.project_dir / relative, True, f"缺少 CI/CD 文件: {relative}")
            for relative in files
        ]

    def _collect_migration_files(self) -> list[Path]:
        patterns = [
            "prisma/migrations/**/*.sql",
            "alembic/versions/*.py",
            "backend/migrations/**/*.sql",
            "backend/migrations/**/*.py",
            "migrations/**/*.sql",
            "src/main/resources/db/migration/*.sql",
        ]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(self.project_dir.glob(pattern))
        return sorted(path for path in files if path.is_file())

    def _build_archive(
        self,
        archive_path: Path,
        included_files: list[str],
        extra_files: list[Path],
    ) -> None:
        with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
            for relative in included_files:
                file_path = self.project_dir / relative
                if file_path.exists():
                    archive.write(file_path, arcname=relative)
            for file_path in extra_files:
                if file_path.exists():
                    arcname = self._relative(file_path)
                    archive.write(file_path, arcname=arcname)

    def _to_markdown(self, manifest: dict[str, object]) -> str:
        status = str(manifest.get("status", "incomplete"))
        status_text = "可交付" if status == "ready" else "未完成"
        included = manifest.get("included_files", [])
        missing = manifest.get("missing_required", [])
        cicd_platform = manifest.get("cicd_platform", "all")

        lines = [
            "# 交付报告",
            "",
            f"- 项目: {manifest.get('project_name', self.name)}",
            f"- 版本: {manifest.get('version', self.version)}",
            f"- 状态: {status_text} ({status})",
            f"- CI/CD 平台: {cicd_platform}",
            f"- 生成时间: {manifest.get('generated_at', '')}",
            "",
            "## 已包含文件",
            "",
        ]

        if isinstance(included, list) and included:
            for item in included:
                lines.append(f"- {item}")
        else:
            lines.append("- (none)")
        lines.append("")

        lines.extend(["## 缺失必需项", ""])
        if isinstance(missing, list) and missing:
            for item in missing:
                if isinstance(item, dict):
                    lines.append(
                        f"- {item.get('path', 'unknown')}: {item.get('reason', '')}"
                    )
        else:
            lines.append("- 无")
        lines.append("")
        return "\n".join(lines)

    def _relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.project_dir))
        except ValueError:
            return str(path)
