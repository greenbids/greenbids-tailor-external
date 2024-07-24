from fastapi import APIRouter, HTTPException, status
from greenbids.tailor.core import models
from greenbids.tailor.core.app import resources

router = APIRouter(prefix="/healthz", tags=["Health check"])


@router.get("/startup")
async def startup_probe() -> resources.AppResources:
    """Verifies whether the application is started."""
    return resources.APP_RESOURCES


@router.get("/liveness")
async def liveness_probe() -> resources.AppResources:
    """Determine when to restart the application."""
    return resources.APP_RESOURCES


@router.get("/readiness")
async def readiness_probe() -> resources.AppResources:
    """Determine when a container is ready to start accepting traffic."""
    if isinstance(resources.APP_RESOURCES.gb_model, models.NullModel):
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY)
    return resources.APP_RESOURCES
