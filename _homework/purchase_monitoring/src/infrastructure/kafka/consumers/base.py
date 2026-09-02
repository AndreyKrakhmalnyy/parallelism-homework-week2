from faststream.kafka import KafkaBroker
from abc import ABC, abstractmethod

from src.infrastructure.kafka.consumers.types import SubscriberParams


class BaseEventConsumer(ABC):
    subscriber_params: SubscriberParams = {}
    
    def __init__(self, broker: KafkaBroker, topic: str, consumer_group: str) -> None:
        self.broker = broker
        self.topic = topic
        self.consumer_group = consumer_group

    @abstractmethod
    async def process_batch(self, messages: list[dict]) -> None: ...
    
    def register(self) -> None:
        self.broker.subscriber(
            self.topic,
            group_id=self.consumer_group,
            **self.subscriber_params
        )(self.process_batch)