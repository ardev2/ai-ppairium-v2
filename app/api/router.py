from fastapi import APIRouter

from .v1 import system

api_router = APIRouter(prefix="/v1")
api_router.include_router(system.router, prefix="/system", tags=["system"])
