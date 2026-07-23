from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException

from app.api.schemas.event import EventCreate, EventDashboard, EventRead
from app.api.dependencies import CurrentUserId
from app.domain.exceptions import DomainError
from app.domain.services.event import EventService

router = APIRouter(prefix="/organizer", route_class=DishkaRoute)

@router.get("/events")
async def list_organizer_events(organizer_id: CurrentUserId) -> list[EventRead]:
    """Возвращает список созданных событий текущего организатора."""
    ...


@router.post("/events")
async def create_event(payload: EventCreate, organizer_id: CurrentUserId) -> EventRead:
    """Создает мероприятие от лица текущего организатора."""
    ...


@router.get("/events/{event_id}/dashboard")
async def get_event_dashboard(
    event_id: int,
    organizer_id: CurrentUserId,
    event_service: FromDishka[EventService],
) -> EventDashboard:
    """Возвращает аналитические данные для дашборда по мероприятию."""
    # TODO: проверить, что мероприятие принадлежит organizer_id.
    # TODO: конкурентно загрузить аналитику продаж и занятость мест отдельными запросами к БД.
    try:
        return await event_service.get_event_stats(event_id, organizer_id)  
    except DomainError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from None