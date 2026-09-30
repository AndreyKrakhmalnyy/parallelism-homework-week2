from src.domain.events.event_payment_activity import EventPaymentActivity
from src.infrastructure.postgres.models import EventPaymentActivity as EventPaymentActivityDB
from src.infrastructure.postgres.repositories.base import BaseRepository
from sqlalchemy.dialects.postgresql import insert as pg_insert


class EventPaymentActivityRepository(BaseRepository):
    async def add_bulk(self, events_payment_activity: list[EventPaymentActivity]) -> None:
        stmt = pg_insert(EventPaymentActivityDB).values([
            {
                "batch_id": event_payment_activity.batch_id,
                "event_id": event_payment_activity.event_id,
                "payments_count": event_payment_activity.payments_count,
                "tickets_count": event_payment_activity.tickets_count,
                "total_amount": event_payment_activity.total_amount,
                "created_at": event_payment_activity.created_at
            } for event_payment_activity in events_payment_activity
        ])
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["event_id"],
            set_={
                "payments_count": EventPaymentActivityDB.payments_count + stmt.excluded.payments_count,
                "tickets_count": EventPaymentActivityDB.tickets_count + stmt.excluded.tickets_count,
                "total_amount": EventPaymentActivityDB.total_amount + stmt.excluded.total_amount
            }
        )
        await self.session.execute(upsert_stmt)