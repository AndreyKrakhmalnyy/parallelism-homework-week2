import logging

from faststream import AckPolicy
from dishka import FromDishka
from dishka_faststream import inject

from src.services.ws_broadcaster import WebsockerBroadcasterService
from src.services.purchase_ticket_aggregation import PurchaseTicketAggregationService
from src.infrastructure.kafka.consumers.base import BaseEventConsumer, SubscriberParams


logger = logging.getLogger(__name__)

class PurchaseTicketConsumer(BaseEventConsumer):
    subscriber_params: SubscriberParams = {
        "batch": True,
        "auto_offset_reset": "earliest",
        "ack_policy": AckPolicy.NACK_ON_ERROR,
        "max_records": 10,
        "batch_timeout_ms": 500,
    }

    @inject
    async def process_batch(
        self, 
        messages: list[dict], 
        ws_broadcaster_service: FromDishka[WebsockerBroadcasterService],
        purchase_ticket_agg_service: FromDishka[PurchaseTicketAggregationService]
    ) -> None:
        """Слушает топик `purchase.ticket`, агрегирует и коммитит брокеру после вставки в БД.
        
        Если есть данные, которые были агрегированы и закоммичены в БД, то рассылает их всем 
        подключенным клиентам через WebSocket.
        """
        logger.info(f"PurchaseTicketConsumer started proccessing, recved {len(messages)} messages")
        commited_events = await purchase_ticket_agg_service.aggregate(messages)
        logger.info("PurchaseTicketConsumer finished processing")
        
        if commited_events:
            await ws_broadcaster_service.broadcast_aggregate_event_payment(commited_events)
            logger.info(f"PurchaseTicketConsumer broadcasted {len(commited_events)} events to WebSocket clients")