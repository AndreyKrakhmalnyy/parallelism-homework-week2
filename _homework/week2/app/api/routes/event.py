from dishka import FromDishka
from fastapi import APIRouter
from app.domain.services.booking import BookingService
from app.api.dependencies import CurrentUserId
from app.api.schemas1 import (
    BookingCreate, 
    EventRead, 
    EventSeatRead
)
from app.api.schemas.booking import CheckoutResponse

router = APIRouter(prefix="/events")


@router.get("/")
async def list_events() -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    ...


@router.get("/events/{event_id}")
async def get_event(event_id: int) -> EventRead:
    """Возвращает описание мероприятия."""
    ...


@router.get("/events/{event_id}/seats")
async def list_event_seats(event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    ...

@router.post("/events/{event_id}/checkout")
async def prepare_checkout(
    event_id: int,
    payload: BookingCreate,
    user_id: CurrentUserId,
    booking_service: FromDishka[BookingService]
) -> CheckoutResponse:
    """Временно бронирует места за клиентом, возвращает итоговую стоимость
        и возможность страховки."""
    # TODO: создать бронь для выбранных мест через SELECT FOR UPDATE, и посчитать базовую стоимость.
    # TODO: конкурентно запросить Payment API и Protection API для расчета checkout.
    ...
