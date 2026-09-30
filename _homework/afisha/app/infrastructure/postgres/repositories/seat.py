from typing import Optional
from sqlalchemy import select
from app.infrastructure.postgres.repositories.base import BaseRepository
from app.infrastructure.postgres.models import Seat


class SeatRepository(BaseRepository):
    async def get_instance_by_id(self, seat_id: int) -> Optional[Seat]:
        query = select(Seat).where(Seat.id == seat_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()
