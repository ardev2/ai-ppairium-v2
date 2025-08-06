from fastapi import APIRouter

from .v1 import system, conversation

api_router = APIRouter(prefix="/v1")
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(
    conversation.router, prefix="/conversation", tags=["conversation"]
)
