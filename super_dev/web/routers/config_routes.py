"""Config, init, and policy routes."""

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from super_dev.catalogs import (
    CICD_PLATFORM_IDS,
    HOST_TOOL_CATALOG,
)
from super_dev.config import ConfigManager
from super_dev.policy import PipelinePolicy, PipelinePolicyManager
from super_dev.web.helpers import _validate_project_dir

CICDPlatform = Literal["github", "gitlab", "jenkins", "azure", "bitbucket", "all"]
VALID_CICD_PLATFORMS: set[str] = set(CICD_PLATFORM_IDS)


class ProjectInitRequest(BaseModel):
    """项目初始化请求"""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=5000)
    platform: str = "web"
    frontend: str = "react"
    backend: str = "node"
    domain: str = ""
    language_preferences: list[str] = []
    quality_gate: int = Field(80, ge=0, le=100)
    host_compatibility_min_score: int = Field(80, ge=0, le=100)
    host_compatibility_min_ready_hosts: int = Field(1, ge=0, le=50)
    host_profile_targets: list[str] = []
    host_profile_enforce_selected: bool = False


class PipelinePolicyResponse(BaseModel):
    require_redteam: bool
    require_quality_gate: bool
    require_rehearsal_verify: bool
    min_quality_threshold: int
    allowed_cicd_platforms: list[str]
    require_host_profile: bool
    required_hosts: list[str]
    enforce_required_hosts_ready: bool
    min_required_host_score: int
    policy_file: str
    policy_exists: bool


class PipelinePolicyUpdateRequest(BaseModel):
    preset: str | None = None
    require_redteam: bool | None = None
    require_quality_gate: bool | None = None
    require_rehearsal_verify: bool | None = None
    min_quality_threshold: int | None = None
    allowed_cicd_platforms: list[str] | None = None
    require_host_profile: bool | None = None
    required_hosts: list[str] | None = None
    enforce_required_hosts_ready: bool | None = None
    min_required_host_score: int | None = None


router = APIRouter()


def _normalize_string_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _build_policy_response(
    policy: PipelinePolicy, manager: PipelinePolicyManager
) -> dict[str, Any]:
    return {
        "require_redteam": policy.require_redteam,
        "require_quality_gate": policy.require_quality_gate,
        "require_rehearsal_verify": policy.require_rehearsal_verify,
        "min_quality_threshold": policy.min_quality_threshold,
        "allowed_cicd_platforms": policy.allowed_cicd_platforms,
        "require_host_profile": policy.require_host_profile,
        "required_hosts": policy.required_hosts,
        "enforce_required_hosts_ready": policy.enforce_required_hosts_ready,
        "min_required_host_score": policy.min_required_host_score,
        "policy_file": str(manager.policy_path),
        "policy_exists": manager.policy_path.exists(),
    }


@router.get("/config")
async def get_config(project_dir: str = ".") -> dict:
    """获取项目配置"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if not manager.exists():
            raise HTTPException(status_code=404, detail="项目未初始化")

        config = manager.config
        return {
            "name": config.name,
            "description": config.description,
            "version": config.version,
            "platform": config.platform,
            "frontend": config.frontend,
            "backend": config.backend,
            "database": config.database,
            "domain": config.domain,
            "language_preferences": config.language_preferences,
            "quality_gate": config.quality_gate,
            "host_compatibility_min_score": config.host_compatibility_min_score,
            "host_compatibility_min_ready_hosts": config.host_compatibility_min_ready_hosts,
            "host_profile_targets": config.host_profile_targets,
            "host_profile_enforce_selected": config.host_profile_enforce_selected,
            "phases": config.phases,
            "experts": config.experts,
            "output_dir": config.output_dir,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy", response_model=PipelinePolicyResponse)
async def get_policy(project_dir: str = ".") -> dict[str, Any]:
    """获取 pipeline policy"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = PipelinePolicyManager(project_dir_path)
        policy = manager.load()
        return _build_policy_response(policy=policy, manager=manager)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policy/presets")
async def list_policy_presets() -> dict[str, Any]:
    """列出可用策略预设"""
    return {
        "presets": [
            {
                "id": "default",
                "description": "默认策略（兼顾灵活性）",
            },
            {
                "id": "balanced",
                "description": "团队协作增强（要求 host profile）",
            },
            {
                "id": "enterprise",
                "description": "商业级强治理（更高质量阈值 + host profile，可按项目配置关键宿主）",
            },
        ]
    }


@router.put("/policy")
async def update_policy(
    request: PipelinePolicyUpdateRequest,
    project_dir: str = ".",
) -> dict[str, Any]:
    """更新 pipeline policy"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = PipelinePolicyManager(project_dir_path)
        preset_name = request.preset.strip().lower() if isinstance(request.preset, str) else ""
        if preset_name:
            current = manager.build_preset(preset_name)
        else:
            current = manager.load()

        min_quality_threshold = current.min_quality_threshold
        if request.min_quality_threshold is not None:
            if request.min_quality_threshold < 0 or request.min_quality_threshold > 100:
                raise HTTPException(
                    status_code=400, detail="min_quality_threshold 必须在 0-100 之间"
                )
            min_quality_threshold = request.min_quality_threshold

        allowed_cicd_platforms = current.allowed_cicd_platforms
        if request.allowed_cicd_platforms is not None:
            normalized = _normalize_string_list(request.allowed_cicd_platforms)
            if not normalized:
                raise HTTPException(status_code=400, detail="allowed_cicd_platforms 不能为空")
            invalid = [item for item in normalized if item not in VALID_CICD_PLATFORMS]
            if invalid:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效 CI/CD 平台: {', '.join(invalid)}",
                )
            allowed_cicd_platforms = normalized

        required_hosts = current.required_hosts
        if request.required_hosts is not None:
            normalized_hosts = _normalize_string_list(request.required_hosts)
            allowed_hosts = {item["id"] for item in HOST_TOOL_CATALOG}
            invalid_hosts = [item for item in normalized_hosts if item not in allowed_hosts]
            if invalid_hosts:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效宿主: {', '.join(invalid_hosts)}",
                )
            required_hosts = normalized_hosts

        min_required_host_score = current.min_required_host_score
        if request.min_required_host_score is not None:
            if request.min_required_host_score < 0 or request.min_required_host_score > 100:
                raise HTTPException(
                    status_code=400, detail="min_required_host_score 必须在 0-100 之间"
                )
            min_required_host_score = request.min_required_host_score

        updated = PipelinePolicy(
            require_redteam=(
                request.require_redteam
                if request.require_redteam is not None
                else current.require_redteam
            ),
            require_quality_gate=(
                request.require_quality_gate
                if request.require_quality_gate is not None
                else current.require_quality_gate
            ),
            require_rehearsal_verify=(
                request.require_rehearsal_verify
                if request.require_rehearsal_verify is not None
                else current.require_rehearsal_verify
            ),
            min_quality_threshold=min_quality_threshold,
            allowed_cicd_platforms=allowed_cicd_platforms,
            require_host_profile=(
                request.require_host_profile
                if request.require_host_profile is not None
                else current.require_host_profile
            ),
            required_hosts=required_hosts,
            enforce_required_hosts_ready=(
                request.enforce_required_hosts_ready
                if request.enforce_required_hosts_ready is not None
                else current.enforce_required_hosts_ready
            ),
            min_required_host_score=min_required_host_score,
        )
        manager.save(updated)
        return _build_policy_response(policy=updated, manager=manager)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init")
async def init_project(request: ProjectInitRequest, project_dir: str = ".") -> dict:
    """初始化项目"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if manager.exists():
            raise HTTPException(status_code=400, detail="项目已初始化")

        config = manager.create(
            name=request.name,
            description=request.description,
            platform=request.platform,
            frontend=request.frontend,
            backend=request.backend,
            domain=request.domain,
            language_preferences=request.language_preferences,
            quality_gate=request.quality_gate,
            host_compatibility_min_score=request.host_compatibility_min_score,
            host_compatibility_min_ready_hosts=request.host_compatibility_min_ready_hosts,
            host_profile_targets=request.host_profile_targets,
            host_profile_enforce_selected=request.host_profile_enforce_selected,
        )

        return {
            "status": "success",
            "message": "项目已初始化",
            "config": {
                "name": config.name,
                "platform": config.platform,
                "frontend": config.frontend,
                "backend": config.backend,
            },
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config")
async def update_config(updates: dict, project_dir: str = ".") -> dict:
    """更新项目配置"""
    try:
        project_dir_path = _validate_project_dir(project_dir)
        manager = ConfigManager(project_dir_path)
        if not manager.exists():
            raise HTTPException(status_code=404, detail="项目未初始化")

        config = manager.update(**updates)
        return {"status": "success", "config": config.__dict__}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
