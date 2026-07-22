from sqlalchemy import select
from typing import Optional
from app.infrastructure.postgres.models import EventSeat
from app.infrastructure.postgres.repositories.base import BaseRepository


class EventSeatRepository(BaseRepository):
    async def get_event_seat_for_update(self, event_id: int, seat_ids: list[int]) -> Optional[EventSeat]:
        query = select(EventSeat).where(EventSeat.event_id == event_id, EventSeat.seat_id.in_(set(seat_ids))).with_for_update()
        orm_data = await self.session.execute(query)
        return orm_data.scalars().all()