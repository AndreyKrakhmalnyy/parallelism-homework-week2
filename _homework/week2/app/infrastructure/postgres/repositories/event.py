from typing import Optional
from sqlalchemy import select
from app.infrastructure.postgres.repositories.base import BaseRepository
from app.infrastructure.postgres.models import Event


class EventRepository(BaseRepository):
    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()