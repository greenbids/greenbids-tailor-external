from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["Connectivity check"])


@router.get("")
async def ping() -> str:
    return "pong"
