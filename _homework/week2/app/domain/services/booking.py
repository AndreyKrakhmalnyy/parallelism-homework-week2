from _homework.week2.app.infrastructure.postgres.repositories.event_seat import EventSeatRepository
from app.domain.exceptions import EventNotFoundError, SeatNotFoundError
from app.api.schemas import CheckoutResponse
from app.infrastructure.postgres.repositories.seat import SeatRepository
from app.infrastructure.postgres.repositories.event import EventRepository


class BookingService:
    def __init__(self, event_repo: EventRepository, seat_repo: SeatRepository, event_seat_repo: EventSeatRepository) -> None:
        self.event_repo = event_repo
        self.seat_repo = seat_repo
        self.event_seat_repo = event_seat_repo
        
    async def create_booking(self, event_id: int, seat_ids: list[int], user_id: int) -> CheckoutResponse:
        event = await self.event_repo.get_event_by_id(event_id=event_id)
        seats = []

        if not event:
            raise EventNotFoundError(event_id)
        
        for seat_id in seat_ids:
            seat = await self.seat_repo.get_seat_by_id(seat_id=seat_id)

            if not seat:
                raise SeatNotFoundError(seat_id)
            else:
                seats.append(seat)     

        if self.event_seat_repo.get_event_seat(event_id=event_id, seat_id=seat_id):
            pass