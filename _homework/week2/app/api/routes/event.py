from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Request
from app.domain.services.event import EventService
from app.domain.exceptions import DomainError
from app.domain.services.booking import BookingService
from app.api.dependencies import CurrentUserId
from app.api.schemas.event import (
    EventRead, 
)
from app.api.schemas.event_seat import EventSeatRead
from app.api.schemas.booking import BookingCreate
from app.api.schemas.booking import CheckoutResponse

router = APIRouter(prefix="/events", route_class=DishkaRoute)


@router.get("/", response_model=list[EventRead], status_code=200)
async def list_events(event_service: FromDishka[EventService]) -> list[EventRead]:
    """Возвращает список мероприятий для клиента."""
    return await event_service.get_list_events()



@router.get("/{event_id}", response_model=EventRead, status_code=200)
async def get_event(event_id: int, event_service: FromDishka[EventService], request: Request) -> EventRead:
    """Возвращает описание мероприятия."""
    try:
        event = await event_service.get_event_by_id(event_id)
    except DomainError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from None

    if request.client:
        await event_service.record_view(event_id, request.client.host)
    return event


@router.get("/{event_id}/seats")
async def list_event_seats(event_id: int) -> list[EventSeatRead]:
    """Возвращает места на мероприятии с ценами и статусами."""
    ...


@router.post("/{event_id}/checkout", response_model=CheckoutResponse, status_code=201)
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
    try:
        booking = await booking_service.reservation_processing(event_id, payload.seat_ids, user_id)
    except DomainError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from None
    return booking
