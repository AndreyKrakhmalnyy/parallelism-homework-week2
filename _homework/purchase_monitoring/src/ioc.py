from typing import AsyncIterator
from src.infrastructure.websocket.manager import WebsocketManager
from src.services.ws_broadcaster import WebsockerBroadcasterService
from src.services.purchase_ticket_aggregation import PurchaseTicketAggregationService
from src.infrastructure.postgres.repositories.event_payment_activity import EventPaymentActivityRepository
from src.infrastructure.kafka.consumers.purchase_ticket import PurchaseTicketConsumer
from src.config import (
    KafkaConfig,
    PostgresConfig,
    PurchaseTicketConsumerConfig,
    Settings
)
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from faststream.kafka import KafkaBroker
from src.infrastructure.postgres.manager import PostgresClient, DatabaseManager


class ConfigProvider(Provider):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return self._settings

    @provide(scope=Scope.APP)
    def get_postgres_config(self, settings: Settings) -> PostgresConfig:
        return settings.postgres

    @provide(scope=Scope.APP)
    def get_kafka_config(self, settings: Settings) -> KafkaConfig:
        return settings.kafka

    @provide(scope=Scope.APP)
    def get_purchase_ticket_consumer_config(self, settings: Settings) -> PurchaseTicketConsumerConfig:
        return settings.kafka.purchase_ticket_consumer

class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_postgres_client(self, config: PostgresConfig) -> AsyncIterator[PostgresClient]:
        client = PostgresClient(config)

        yield client

        await client.close()

    @provide(scope=Scope.REQUEST)
    async def get_db_manager(self, client: PostgresClient) -> AsyncIterator[DatabaseManager]:
        async with client.session() as db:
            yield db

    @provide(scope=Scope.REQUEST)
    def get_session(self, db: DatabaseManager) -> AsyncSession:
        return db.session

class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_event_payment_activity_repo(self, session: AsyncSession) -> EventPaymentActivityRepository:
        return EventPaymentActivityRepository(session)

class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_purchase_ticket_aggregation_service(
        self,
        db: DatabaseManager,
    ) -> PurchaseTicketAggregationService:
        return PurchaseTicketAggregationService(db)

    @provide
    def get_websocket_broadcaster_service(
        self,
        ws_manager: WebsocketManager,
    ) -> "WebsockerBroadcasterService":
        return WebsockerBroadcasterService(ws_manager)


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    def get_kafka_broker(self, config: KafkaConfig) -> KafkaBroker:
        return KafkaBroker(bootstrap_servers=config.bootstrap_server)

        
class EventConsumerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_purchase_ticket_consumer(
        self, 
        broker: KafkaBroker, 
        config: PurchaseTicketConsumerConfig
    ) -> PurchaseTicketConsumer:
        consumer = PurchaseTicketConsumer(
            broker=broker,
            topic=config.topic,
            consumer_group=config.group_id
        )
        consumer.register()
        return consumer


class WebsocketProvider(Provider):
    scope = Scope.APP
    
    @provide
    def get_ws_manager(self) -> WebsocketManager:
        return WebsocketManager()