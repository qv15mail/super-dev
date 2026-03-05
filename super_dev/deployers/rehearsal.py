"""
发布演练（Launch Rehearsal）文档生成器
"""

from __future__ import annotations

from pathlib import Path


class LaunchRehearsalGenerator:
    """生成发布演练清单与回滚手册"""

    def __init__(self, project_dir: Path, name: str, tech_stack: dict[str, str]):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack

    def generate(self, cicd_platform: str) -> dict[str, str]:
        files: dict[str, str] = {}
        base = "output/rehearsal"
        files[f"{base}/{self.name}-launch-rehearsal.md"] = self._build_launch_rehearsal(cicd_platform)
        files[f"{base}/{self.name}-rollback-playbook.md"] = self._build_rollback_playbook(cicd_platform)
        files[f"{base}/{self.name}-smoke-checklist.md"] = self._build_smoke_checklist()
        return files

    def _build_launch_rehearsal(self, cicd_platform: str) -> str:
        return f"""# Launch Rehearsal

- Project: `{self.name}`
- Platform: `{self.tech_stack.get('platform', 'web')}`
- Frontend: `{self.tech_stack.get('frontend', 'react')}`
- Backend: `{self.tech_stack.get('backend', 'node')}`
- CI/CD: `{cicd_platform}`

## Objectives

1. Validate deployment workflow end-to-end in a pre-production environment.
2. Verify rollback path within target recovery time.
3. Confirm observability and alert thresholds after release.

## Pre-flight Gate

- [ ] Red-team report passed (no critical blockers)
- [ ] Quality gate score >= 80
- [ ] Spec task execution report has no unresolved blockers
- [ ] Database migration dry-run passed
- [ ] CI pipeline green on release commit

## Rehearsal Timeline

1. Freeze release candidate commit.
2. Deploy to staging using same workflow as production.
3. Run smoke checklist and synthetic transactions.
4. Trigger rollback simulation.
5. Re-deploy and verify recovery.
6. Record outcomes and decision log.
"""

    def _build_rollback_playbook(self, cicd_platform: str) -> str:
        return f"""# Rollback Playbook

- Project: `{self.name}`
- CI/CD: `{cicd_platform}`

## Trigger Conditions

- [ ] Error rate spike over agreed SLO threshold
- [ ] P95 latency regression over threshold
- [ ] Authentication or payment critical flow failure
- [ ] Data integrity check failed

## Rollback Procedure

1. Halt current rollout / traffic shift.
2. Restore previous stable image/tag.
3. Revert incompatible migrations (or apply compensating migration).
4. Re-run smoke checks on rolled-back version.
5. Communicate status and incident scope.

## Required Evidence

- Incident start/end timestamps
- Metrics snapshots before and after rollback
- Root-cause hypothesis
- Permanent fix owner and ETA
"""

    def _build_smoke_checklist(self) -> str:
        return """# Smoke Checklist

## Core Availability

- [ ] Health endpoint returns 200
- [ ] Frontend entry page renders without blocking errors
- [ ] Core API auth flow (login/token refresh) works

## Business Critical Flows

- [ ] Primary create/read/update flow passes
- [ ] One payment/order workflow passes (if applicable)
- [ ] One admin workflow passes

## Reliability and Security

- [ ] Error budget burn within expected range
- [ ] No new critical security findings
- [ ] Alerting rules and dashboards are active
"""

