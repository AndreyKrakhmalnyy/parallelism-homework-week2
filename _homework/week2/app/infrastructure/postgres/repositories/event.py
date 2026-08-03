from typing import Optional
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.infrastructure.postgres.repositories.base import BaseRepository
from app.infrastructure.postgres.models import Event, EventView


class EventRepository(BaseRepository):
    async def get_list_events(self) -> list[Event]:
        orm_data = await self.session.execute(select(Event))
        return list(orm_data.scalars().all())

    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()
    
    async def get_event_by_organizer_id(self, event_id: int, organizer_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id, Event.organizer_id == organizer_id)
        orm_data = await self.session.execute(query)
        return orm_data.scalar_one_or_none()

    async def add_event_views_bulk(self, events_views: list[EventView]):
        stmt = pg_insert(EventView).values([{"event_id": ev_view.event_id, "views_count": ev_view.views_count} for ev_view in events_views])
        upsert_stmt = stmt.on_conflict_do_update(index_elements=["event_id"], set_={"views_count": EventView.views_count + stmt.excluded.views_count})
        await self.session.execute(upsert_stmt)