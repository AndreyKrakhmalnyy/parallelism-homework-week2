from sqlalchemy import func, select
from typing import Optional
from app.domain.enums import SeatStatus
from app.infrastructure.postgres.dto import OccupancySummary
from app.infrastructure.postgres.models import EventSeat
from app.infrastructure.postgres.repositories.base import BaseRepository


class EventSeatRepository(BaseRepository):
    async def get_event_seat_for_update(self, event_id: int, seat_ids: list[int]) -> Optional[EventSeat]:
        query = select(EventSeat).where(EventSeat.event_id == event_id, EventSeat.seat_id.in_(set(seat_ids))).with_for_update()
        orm_data = await self.session.execute(query)
        return orm_data.scalars().all()

    async def count_sold(self, event_id: int) -> int:
        query = select(func.count(EventSeat.id)).where(
            EventSeat.event_id == event_id,
            EventSeat.status == SeatStatus.sold,
        )
        return await self.session.scalar(query)

    async def get_occupancy_summary(self, event_id: int) -> OccupancySummary:
        query = (
            select(EventSeat.status, func.count(EventSeat.id))
            .where(EventSeat.event_id == event_id)
            .group_by(EventSeat.status)
        )
        rows = (await self.session.execute(query)).all()
        counts = dict(rows)
        return OccupancySummary(
            total=sum(counts.values()),
            available=counts.get(SeatStatus.available, 0),
            reserved=counts.get(SeatStatus.reserved, 0),
            sold=counts.get(SeatStatus.sold, 0),
        )
    
    async def get_event_seats_by_booking_id(self, booking_id: int) -> list[EventSeat]:
        query = select(EventSeat).where(EventSeat.booking_id == booking_id)
        orm_data = await self.session.execute(query)
        return list(orm_data.scalars().all())