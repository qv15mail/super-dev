# API Contract

当前仓库的后端/服务接口主要由 `super_dev/web/api.py` 暴露。以下为当前可观测路由摘要。

| Method | Path | Purpose |
|:---|:---|:---|
| GET | /api/health | Super Dev Studio / release / review surface |
| GET | /api/config | Super Dev Studio / release / review surface |
| GET | /api/policy", response_model=PipelinePolicyResponse | Super Dev Studio / release / review surface |
| GET | /api/policy/presets | Super Dev Studio / release / review surface |
| PUT | /api/policy", response_model=PipelinePolicyResponse | Super Dev Studio / release / review surface |
| POST | /api/init | Super Dev Studio / release / review surface |
| PUT | /api/config | Super Dev Studio / release / review surface |
| POST | /api/workflow/run | Super Dev Studio / release / review surface |
| GET | /api/workflow/status/{run_id} | Super Dev Studio / release / review surface |
| GET | /api/workflow/docs-confirmation | Super Dev Studio / release / review surface |
| POST | /api/workflow/docs-confirmation | Super Dev Studio / release / review surface |
| GET | /api/workflow/ui-revision | Super Dev Studio / release / review surface |
| POST | /api/workflow/ui-revision | Super Dev Studio / release / review surface |
| GET | /api/workflow/architecture-revision | Super Dev Studio / release / review surface |
| POST | /api/workflow/architecture-revision | Super Dev Studio / release / review surface |
| GET | /api/workflow/quality-revision | Super Dev Studio / release / review surface |
| POST | /api/workflow/quality-revision | Super Dev Studio / release / review surface |
| POST | /api/workflow/cancel/{run_id} | Super Dev Studio / release / review surface |
| GET | /api/workflow/runs | Super Dev Studio / release / review surface |
| GET | /api/workflow/artifacts/{run_id} | Super Dev Studio / release / review surface |
| GET | /api/workflow/artifacts/{run_id}/archive | Super Dev Studio / release / review surface |
| GET | /api/workflow/ui-review/{run_id} | Super Dev Studio / release / review surface |
| GET | /api/workflow/ui-review/{run_id}/screenshot | Super Dev Studio / release / review surface |
| GET | /api/experts | Super Dev Studio / release / review surface |
| POST | /api/experts/{expert_id}/advice | Super Dev Studio / release / review surface |
| GET | /api/experts/advice/history | Super Dev Studio / release / review surface |
| GET | /api/experts/advice/content | Super Dev Studio / release / review surface |
| GET | /api/phases | Super Dev Studio / release / review surface |
| GET | /api/catalogs | Super Dev Studio / release / review surface |
| GET | /api/hosts/doctor | Super Dev Studio / release / review surface |
| GET | /api/hosts/validate | Super Dev Studio / release / review surface |
| GET | /api/hosts/runtime-validation | Super Dev Studio / release / review surface |
| POST | /api/hosts/runtime-validation | Super Dev Studio / release / review surface |
| GET | /api/deploy/platforms | Super Dev Studio / release / review surface |
| GET | /api/deploy/precheck | Super Dev Studio / release / review surface |
| GET | /api/deploy/remediation | Super Dev Studio / release / review surface |
| POST | /api/deploy/remediation/export | Super Dev Studio / release / review surface |
| GET | /api/deploy/remediation/archive | Super Dev Studio / release / review surface |
| POST | /api/deploy/generate | Super Dev Studio / release / review surface |
| GET | /api/release/readiness | Super Dev Studio / release / review surface |
| GET | /api/release/proof-pack | Super Dev Studio / release / review surface |
| GET | /api/analyze/repo-map | Super Dev Studio / release / review surface |
| GET | /api/analyze/impact | Super Dev Studio / release / review surface |
| GET | /api/analyze/regression-guard | Super Dev Studio / release / review surface |
| GET | /api/analyze/dependency-graph | Super Dev Studio / release / review surface |
