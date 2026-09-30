from api.routes.ws_broadcaster import router as ws_router
from fastapi import APIRouter

__all__ = ("main_router",)

main_router = APIRouter()

main_router.include_router(ws_router)