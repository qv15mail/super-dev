"""Health check router."""

from fastapi import APIRouter

from super_dev import __version__

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": __version__}


@router.get("/health/root")
async def health_check_root():
    """健康检查 (root alias for k8s probes and load balancers)"""
    return {"status": "healthy", "version": __version__}
