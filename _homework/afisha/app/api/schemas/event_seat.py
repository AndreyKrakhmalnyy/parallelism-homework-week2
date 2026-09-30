from datetime import datetime
from pydantic import BaseModel

from app.domain.enums import SeatStatus


class EventSeatRead(BaseModel):
    id: int
    event_id: int
    seat_id: int
    sector: str
    row: int
    number: int
    x: int
    y: int
    price: int
    status: SeatStatus
    reserved_until: datetime | None
    booking_id: int | None
