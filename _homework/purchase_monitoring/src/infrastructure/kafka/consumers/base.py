from faststream.kafka import KafkaBroker
from abc import ABC, abstractmethod


class BaseEventConsumer(ABC):
    def __init__(self, broker: KafkaBroker, topic: str) -> None:
        self.broker = broker
        self.topic = topic
