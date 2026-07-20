from sqlalchemy import select
from typing import Optional
from app.infrastructure.postgres.models import EventSeat
from app.infrastructure.postgres.repositories.base import BaseRepository


class EventSeatRepository(BaseRepository):
    async def get_event_seat(self, event_id: int, seat_id: int) -> Optional[EventSeat]:
        query = select(EventSeat).where(EventSeat.event_id == event_id, EventSeat.seat_id == seat_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()