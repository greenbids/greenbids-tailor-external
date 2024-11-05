from fastapi import APIRouter, HTTPException, status
from greenbids.tailor.core.app import resources

router = APIRouter(prefix="/healthz", tags=["Health check"])


@router.get("/startup")
async def startup_probe() -> resources.AppResources:
    """Verifies whether the application is started."""
    return resources.get_instance()


@router.get("/liveness")
async def liveness_probe() -> resources.AppResources:
    """Determine when to restart the application."""
    return resources.get_instance()


@router.get("/readiness")
async def readiness_probe() -> resources.AppResources:
    """Determine when a container is ready to start accepting traffic."""
    instance = resources.get_instance()
    if not instance.is_ready:
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY)
    return instance
