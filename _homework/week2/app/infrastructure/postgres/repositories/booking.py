from app.infrastructure.postgres.models import Booking
from app.infrastructure.postgres.repositories.base import BaseRepository


class BookingRepository(BaseRepository):
    async def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.flush()
        return booking