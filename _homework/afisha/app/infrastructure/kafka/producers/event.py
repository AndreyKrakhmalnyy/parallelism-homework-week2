import random
from datetime import datetime
from dataclasses import asdict
from typing import Union
import uuid

from app.infrastructure.kafka.producers.dto import PaymentTicketDTO
from app.infrastructure.kafka.producers.base import BaseEventProducer


class PaymentTicketPublisher(BaseEventProducer):
    BATCH_SIZE = 20

    async def publish_batch(self) -> int:
        messages = self._generate_ticket_payments(self.BATCH_SIZE)
        await super().publish_batch(messages)
        return len(messages)

    def _generate_ticket_payments(self, batch_count: int) -> list[dict[str, Union[int, uuid.uuid4, datetime]]]:
        return [
            asdict(
                PaymentTicketDTO(
                    event_id=random.randint(1, 5), 
                    tickets_count=i, total_amount=i * 500
                )
            )
            for i in range(1, batch_count)
        ]   