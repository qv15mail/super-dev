from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


STAGE_ORDER = [
    "requirement",
    "design",
    "architecture",
    "implementation",
    "testing",
    "security",
    "release",
    "operations",
    "incident_learning",
    "governance",
]


def _load_template_catalog(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Template catalog not found: {path}")
    mapping: dict[str, str] = {}
    current_stage = ""
    in_catalog = False
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.strip() == "template_catalog:":
            in_catalog = True
            continue
        if not in_catalog:
            continue
        if raw.startswith("  ") and raw.strip().endswith(":") and not raw.startswith("    "):
            current_stage = raw.strip()[:-1]
            continue
        if raw.startswith("    file:") and current_stage:
            file_name = raw.split(":", 1)[1].strip()
            mapping[current_stage] = file_name
    return mapping


def _select_stages(catalog: dict[str, str], stages: list[str]) -> list[str]:
    if not stages:
        return [stage for stage in STAGE_ORDER if stage in catalog]
    missing = [stage for stage in stages if stage not in catalog]
    if missing:
        raise ValueError(f"Unknown stages: {', '.join(missing)}")
    return stages


def run(project_dir: Path, output_dir: Path, packet_name: str, stages: list[str], force: bool) -> tuple[bool, str]:
    template_root = project_dir / "knowledge" / "development" / "15-lifecycle-templates"
    catalog = _load_template_catalog(template_root / "template-catalog.yaml")
    selected_stages = _select_stages(catalog, stages)
    packet_root = output_dir / packet_name
    if packet_root.exists():
        if not force:
            return False, f"Packet already exists: {packet_root}"
        shutil.rmtree(packet_root)
    packet_root.mkdir(parents=True, exist_ok=True)
    generated_files: list[str] = []
    for idx, stage in enumerate(selected_stages, start=1):
        source = template_root / catalog[stage]
        if not source.exists():
            return False, f"Template file missing: {source}"
        target = packet_root / f"{idx:02d}-{stage}.md"
        target.write_text(source.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        generated_files.append(str(target))
    manifest = {
        "packet_name": packet_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stages": selected_stages,
        "files": generated_files,
    }
    (packet_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, f"Generated lifecycle packet: {packet_root}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate lifecycle delivery packet from templates.")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--output-dir", default="artifacts/lifecycle-packets", help="Output directory")
    parser.add_argument("--name", required=True, help="Packet name")
    parser.add_argument("--stages", default="", help="Comma-separated stages")
    parser.add_argument("--force", action="store_true", help="Overwrite existing packet")
    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    stages = [item.strip() for item in args.stages.split(",") if item.strip()]
    ok, message = run(
        project_dir=project_dir,
        output_dir=output_dir,
        packet_name=args.name.strip(),
        stages=stages,
        force=args.force,
    )
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
