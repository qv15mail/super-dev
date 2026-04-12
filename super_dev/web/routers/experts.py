"""Experts router — all /api/experts/* routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from super_dev.experts import (
    has_expert,
    list_expert_advice_history,
    read_expert_advice,
    save_expert_advice,
)
from super_dev.experts import (
    list_experts as list_expert_catalog,
)
from super_dev.web.helpers import _validate_project_dir


class ExpertAdviceRequest(BaseModel):
    """专家建议请求"""

    prompt: str = ""


router = APIRouter()


@router.get("/experts")
async def list_experts() -> dict:
    """列出可用专家"""
    return {"experts": list_expert_catalog()}


@router.post("/experts/{expert_id}/advice")
async def generate_expert_advice(
    expert_id: str,
    request: ExpertAdviceRequest,
    project_dir: str = ".",
) -> dict:
    """生成专家建议并写入 output 目录。"""
    expert_id = expert_id.upper()
    if not has_expert(expert_id):
        raise HTTPException(status_code=404, detail=f"未知专家: {expert_id}")

    project_dir_path = _validate_project_dir(project_dir)
    file_path, content = save_expert_advice(
        project_dir=project_dir_path,
        expert_id=expert_id,
        prompt=request.prompt,
    )
    return {
        "expert_id": expert_id,
        "project_dir": str(project_dir_path),
        "file_path": str(file_path),
        "file_name": file_path.name,
        "content": content,
    }


@router.get("/experts/advice/history")
async def get_expert_advice_history(project_dir: str = ".", limit: int = 20) -> dict:
    """列出已生成的专家建议历史。"""
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit 必须大于 0")
    if limit > 500:
        limit = 500

    project_dir_path = _validate_project_dir(project_dir)
    items = list_expert_advice_history(project_dir_path, limit=limit)
    return {"items": items, "count": len(items)}


@router.get("/experts/advice/content")
async def get_expert_advice_content(file_name: str, project_dir: str = ".") -> dict:
    """读取某个专家建议内容。"""
    project_dir_path = _validate_project_dir(project_dir)
    try:
        file_path, content = read_expert_advice(project_dir_path, file_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"建议文件不存在: {file_name}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "content": content,
    }


@router.get("/experts/{name}")
async def get_expert(name: str, project_dir: str = ".") -> dict[str, Any]:
    """Get a specific expert definition."""
    try:
        from super_dev.orchestrator.experts import EXPERT_PROFILES, ExpertRole

        name_upper = name.upper()
        try:
            role = ExpertRole(name_upper)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Unknown expert: {name}")
        profile = EXPERT_PROFILES.get(role)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Expert profile not found: {name}")
        return {
            "status": "success",
            "data": {
                "role": profile.role.value,
                "title": profile.title,
                "goal": profile.goal,
                "backstory": profile.backstory,
                "focus_areas": profile.focus_areas,
                "thinking_framework": profile.thinking_framework,
                "quality_criteria": profile.quality_criteria,
            },
        }
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=501, detail="experts module not available")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
