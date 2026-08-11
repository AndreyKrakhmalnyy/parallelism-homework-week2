import asyncio
from datetime import timedelta
import logging

from app.domain.enums import BookingStatus
from app.infrastructure.postgres.manager import DatabaseManager
from app.api.schemas.protection import ProtectionQuoteIn
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.domain.services.booking import BookingService
from app.ioc import create_container
from app.reports.pdf_reports import PDF_REPORT_PATH, generate_event_dashboard_pdf
from app.api.schemas.event import EventDashboard
from app.infrastructure.taskiq.app import cpu_broker, asyncio_broker
from app.config import settings

logger = logging.getLogger(__name__)


@cpu_broker.task(
    task_name="generate_event_dashboard_report",
    max_retries=3,
    retry_on_error=True,
)
async def generate_event_dashboard_report(event_id: int, event_dashboard: EventDashboard) -> None:
    logger.info("Report formation started")
    generate_event_dashboard_pdf(
        event_id=event_id,
        dashboard=event_dashboard,
        output_path=PDF_REPORT_PATH,
    )
    logger.info("Report formation finished")


@asyncio_broker.task(
    task_name="cancel_expired_bookings",
    schedule=[
        {
            "schedule_id": "cancel_expired_bookings_every_minute",
            "interval": timedelta(minutes=1),
        }
    ],
)
async def cancel_expired_bookings() -> None:
    container = create_container(settings)
    async with container() as app_container:
        booking_service = await app_container.get(BookingService)
        logger.info("Booking cancelling started")
        task_result = await booking_service.cancel_expired_bookings()
        logger.info(f"Booking cancelling finished, cancelled {task_result.get("deleted_count")} booking")


@asyncio_broker.task(
    task_name="get_protection_price",
    max_retries=2,
    retry_on_error=True,
)
async def get_protection_price(payload: ProtectionQuoteIn) -> None:
    container = create_container(settings)
    async with container() as app_container:
        protection_connector = await app_container.get(ProtectionConnector)
        db_manager = await app_container.get(DatabaseManager)

        result = await protection_connector.calculate(payload)

        if result:
            booking = await db_manager.booking_repo.get_by_id(payload.booking_id)

            if booking and booking.status == BookingStatus.pending_payment:
                booking.protection_price = result.price
                booking.with_protection = True
                db_manager.session.commit()
