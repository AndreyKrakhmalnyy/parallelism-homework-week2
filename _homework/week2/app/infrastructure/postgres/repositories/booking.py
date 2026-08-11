from typing import Optional
from sqlalchemy import func, select, delete
from app.infrastructure.postgres.dto import SalesSummary
from app.domain.enums import BookingStatus
from app.infrastructure.postgres.models import Booking
from app.infrastructure.postgres.repositories.base import BaseRepository


class BookingRepository(BaseRepository):
    async def get_list(self) -> list[Booking]:
        orm_data = await self.session.execute(select(Booking))
        return list(orm_data.scalars().all())
    
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        query = select(Booking).where(Booking.id == booking_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()
    
    async def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.flush()
        return booking

    async def get_sales_summary(self, event_id: int) -> SalesSummary:
        query = select(
            func.count(Booking.id),
            func.coalesce(func.sum(Booking.amount + Booking.payment_commission), 0),
        ).where(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.paid,
        )
        paid_orders, revenue = (await self.session.execute(query)).one()
        return SalesSummary(paid_orders=paid_orders, revenue=revenue)
    
    async def delete_by_id(self, booking_id: int) -> None:
        await self.session.execute(delete(Booking).where(Booking.id == booking_id))