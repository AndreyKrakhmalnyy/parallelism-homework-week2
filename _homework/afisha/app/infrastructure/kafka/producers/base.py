from faststream.kafka import KafkaBroker, KafkaPublishMessage
from abc import ABC, abstractmethod


class BaseEventProducer(ABC):
    def __init__(self, broker: KafkaBroker, topic: str) -> None:
        self.broker = broker
        self.topic = topic
    
    @abstractmethod
    async def publish_batch(self, messages: list[dict]) -> None:
        await self.broker.publish_batch(
            *[
                KafkaPublishMessage(message, key=str(message["event_id"]).encode())
                for message in messages
            ],
            topic=self.topic
        )
