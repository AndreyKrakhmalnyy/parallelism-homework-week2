import logging
from typing import Any, Union

from pydantic import ValidationError

from src.infrastructure.postgres.manager import DatabaseManager
from src.domain.dto.purchase import PurchaseTicket
from src.domain.events.event_payment_activity import EventPaymentActivity
from collections import defaultdict

logger = logging.getLogger(__name__)


class PurchaseTicketAggregationService:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager

    async def aggregate(self, purchase_tickets: list[dict]) -> Union[list[Any], list[EventPaymentActivity]]:
        """Агрегирует покупки билетов по мероприятиям и коммитит в БД (массовая вставка).
        
        Сначала валидирует данные сообщения через `pydantic` модель, отсеивая невалидные
        сообщения и логирует ошибки. Далее агрегирует данные для каждого мероприятия
        по `event_id` и формирует список `EventPaymentActivity`, который затем коммитится в БД.
        
        Коммитятся только те, которые прошли валидацию.
        """
        valid_data = []
        
        for purchase_ticket in purchase_tickets:
            try:
                validate = PurchaseTicket.model_validate(purchase_ticket)
            except ValidationError as e:
                logger.error("Invalid purchase ticket data: %s", str(e))
                continue
            valid_data.append(validate)
                
        if not valid_data: return []
        
        mapper= defaultdict(lambda: {
            "payments_count": 0,
            "tickets_count": 0,
            "total_amount": 0
        })
        
        for dto in valid_data:
            event_data = mapper[dto.event_id]
            event_data["payments_count"] += 1
            event_data["tickets_count"] += dto.tickets_count
            event_data["total_amount"] += dto.total_amount
        result: list[EventPaymentActivity] = [
            EventPaymentActivity(
                event_id=event_id,
                payments_count=data["payments_count"],
                tickets_count=data["tickets_count"],
                total_amount=data["total_amount"]
            ) for event_id, data in mapper.items()
        ]
        await self.db_manager.event_payment_activity_repo.add_bulk(result)
        await self.db_manager.commit()
        logger.info(f"Aggregated {len(result)} events from {len(valid_data)} purchase tickets and added to DB")
        return result
