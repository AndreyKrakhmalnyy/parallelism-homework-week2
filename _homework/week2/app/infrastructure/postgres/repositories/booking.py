from sqlalchemy import func, select
from app.infrastructure.postgres.dto import SalesSummary
from app.domain.enums import BookingStatus
from app.infrastructure.postgres.models import Booking
from app.infrastructure.postgres.repositories.base import BaseRepository


class BookingRepository(BaseRepository):
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