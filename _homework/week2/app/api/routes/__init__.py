from fastapi import APIRouter
from app.api.routes.booking import router as booking_router
from app.api.routes.event import router as event_router
from app.api.routes.location import router as location_router
from app.api.routes.organizer import router as organizer_router

__all__ = ("main_router",)

main_router = APIRouter()

main_router.include_router(booking_router)
main_router.include_router(event_router)
main_router.include_router(location_router)
main_router.include_router(organizer_router)