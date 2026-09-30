from datetime import timedelta
import logging

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from app.infrastructure.kafka.producers.purchase_ticket import PurchaseTicketProducer
from app.services.booking import BookingService
from app.infrastructure.taskiq.brokers import asyncio_broker

logger = logging.getLogger(__name__)


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
    task_name="generate_payment_ticket_events",
    schedule=[
        {
            "schedule_id": "generate_payment_ticket_events",
            "interval": timedelta(seconds=30)
        }
    ]
)
@inject
async def generate_payment_ticket_events(
    payment_ticket_publisher: FromDishka[PurchaseTicketProducer]
) -> None:
    """Генерирует события о покупках билетов на мероприятия и публикует брокеру в топик `purchase.ticket`"""
    logger.info("Generate test payment-ticket events started")
    messages_count = await payment_ticket_publisher.publish_batch()
    logger.info("Generate test payment-ticket events finished, published events: %s", messages_count)