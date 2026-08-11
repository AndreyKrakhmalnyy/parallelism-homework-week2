from asyncio import TaskGroup
from app.infrastructure.postgres.dto import OccupancySummary, SalesSummary
from app.domain.exceptions import EventNotFoundError
from app.infrastructure.postgres.manager import DatabaseManager
from app.api.schemas.event import EventDashboard, EventRead, OccupancyDashboard, SalesDashboard


class EventService:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    async def get_list(self) -> list[EventRead]:
        result = await self.db_manager.event_repo.get_list()
        return [EventRead.model_validate(event) for event in result]

    async def get_event_stats(self, event_id: int, organizer_id: int) -> EventDashboard:
        event = await self.db_manager.event_repo.get_by_organizer_id(event_id, organizer_id)
        if not event:
            raise EventNotFoundError(event_id=event_id)

        async with TaskGroup() as tg:
            sales_summary_task = tg.create_task(self._get_sales_summary(event_id))
            sold_tickets_task = tg.create_task(self._get_sold_tickets(event_id))
            occupancy_summary_task = tg.create_task(self._get_occupancy_summary(event_id))
        sales_summary = sales_summary_task.result()
        sold_tickets = sold_tickets_task.result()
        occupancy_summary = occupancy_summary_task.result()

        average_order = sales_summary.revenue // sales_summary.paid_orders if sales_summary.paid_orders else 0
        occupancy_percent = (occupancy_summary.sold / occupancy_summary.total * 100) if occupancy_summary.total else 0.0

        occupancy = OccupancyDashboard(
            total=occupancy_summary.total,
            available=occupancy_summary.available,
            reserved=occupancy_summary.reserved,
            sold=occupancy_summary.sold,
            occupancy_percent=occupancy_percent
        )
        sales = SalesDashboard(
            paid_orders=sales_summary.paid_orders,
            sold_tickets=sold_tickets,
            revenue=sales_summary.revenue,
            average_order=average_order,
        )
        return EventDashboard(
            event_title=event.title,
            starts_at=event.starts_at,
            sales=sales,
            occupancy=occupancy,
        )

    async def _get_sales_summary(self, event_id: int) -> SalesSummary:
        async with self.db_manager.transaction() as db_manager:
            sales_summary = await db_manager.booking_repo.get_sales_summary(event_id)
            return sales_summary
    
    async def _get_sold_tickets(self, event_id: int) -> int:
        async with self.db_manager.transaction() as db_manager:
            count_sold = await db_manager.event_seat_repo.count_sold(event_id)
            return count_sold

    async def _get_occupancy_summary(self, event_id: int) -> OccupancySummary:
        async with self.db_manager.transaction() as db_manager:
            return await db_manager.event_seat_repo.get_occupancy_summary(event_id)
