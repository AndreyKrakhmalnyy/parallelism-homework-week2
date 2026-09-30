from dataclasses import asdict
import random
from datetime import datetime
from typing import Union
import uuid

from app.domain.events.purchase import PurchaseTicket
from app.infrastructure.kafka.producers.base import BaseEventProducer


class PurchaseTicketProducer(BaseEventProducer):
    BATCH_SIZE = 20

    async def publish_batch(self) -> int:
        messages = self._generate_ticket_purchases(self.BATCH_SIZE)
        await super().publish_batch(messages)
        return len(messages)

    def _generate_ticket_purchases(self, batch_count: int) -> list[dict[str, Union[int, uuid.UUID, datetime]]]:
        """Генерирует рандомные события о покупках билетов"""
        return [
            asdict(
                PurchaseTicket(
                    event_id=random.randint(1, 5), 
                    tickets_count=i, total_amount=i * 500
                )
            )
            for i in range(1, batch_count + 1)
        ]   