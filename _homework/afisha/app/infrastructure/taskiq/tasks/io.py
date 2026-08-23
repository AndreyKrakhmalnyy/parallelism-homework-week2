
import logging

import httpx
from dishka import FromDishka
from dishka.integrations.taskiq import inject

from app.api.schemas.protection import ProtectionQuoteIn
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.services.booking import BookingService
from app.infrastructure.taskiq.brokers import asyncio_broker

logger = logging.getLogger(__name__)


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
