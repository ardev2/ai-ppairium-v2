from fastapi import APIRouter
from config.settings import settings

router = APIRouter()


@router.get("/info")
def api_info():
    return {"version": settings.APP_VERSION, "features": [""]}


@router.get("/health")
def api_health():
    return {"status": "ok", "database": "connected"}
