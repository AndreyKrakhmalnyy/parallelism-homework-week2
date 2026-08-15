from datetime import timedelta
import logging

import httpx
from dishka import FromDishka
from dishka.integrations.taskiq import inject

from app.api.schemas.protection import ProtectionQuoteIn
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.domain.services.booking import BookingService
from app.reports.pdf_reports import PDF_REPORT_PATH, generate_event_dashboard_pdf
from app.api.schemas.event import EventDashboard
from app.infrastructure.taskiq.brokers import cpu_broker, asyncio_broker

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
@inject
async def cancel_expired_bookings(booking_service: FromDishka[BookingService]) -> None:
    logger.info("Booking cancelling started")
    task_result = await booking_service.cancel_expired_bookings()
    logger.info(f"Booking cancelling finished, cancelled {task_result.get("deleted_count")} booking")


@asyncio_broker.task(
    task_name="sync_protection_price",
    max_retries=2,
    retry_on_error=True,
)
@inject
async def sync_protection_price(
    payload: ProtectionQuoteIn,
    protection_connector: FromDishka[ProtectionConnector],
    booking_service: FromDishka[BookingService],
) -> None:
    try:
        result = await protection_connector.calculate(payload)
    except (httpx.NetworkError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
        logger.error("Protection API request error: %s", str(e))
        raise

    if result:
        await booking_service.set_protection_price(payload.booking_id, result)
