from pathlib import Path
from typing import AsyncIterator, Union
from app.reports.pdf_reports import generate_event_dashboard_pdf
from app.api.schemas.event import EventDashboard
from app.infrastructure.redis.manager import RedisManager, create_redis_manager
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.infrastructure.api_connectors.external.payment import PaymentConnector
from app.infrastructure.postgres.repositories.seat import SeatRepository
from app.infrastructure.postgres.repositories.event import EventRepository
from app.domain.services.booking import BookingService
from app.domain.services.event import EventService
from app.config import (
    ConnectorsConfig,
    PostgresConfig,
    RedisConfig,
    Settings
)
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from app.infrastructure.postgres.manager import DatabaseManager, PostgresClient
from sqlalchemy.ext.asyncio import AsyncSession


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
    def get_connectors_config(self, settings: Settings) -> ConnectorsConfig:
        return settings.connectors

    @provide(scope=Scope.APP)
    def get_redis_config(self, settings: Settings) -> RedisConfig:
        return settings.redis

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
    def get_event_repo(self, session: AsyncSession) -> EventRepository:
        return EventRepository(session)
    
    @provide
    def get_seat_repo(self, session: AsyncSession) -> SeatRepository:
        return SeatRepository(session)
    

class ConnectorProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_payment_connector(self, config: ConnectorsConfig) -> AsyncIterator[PaymentConnector]:
        payment = config.payment
        connector = PaymentConnector(
            base_url=payment.base_url,
            timeout=payment.timeout,
            retry_count=payment.retry_count
        )
        yield connector
        await connector.close_connection()

    @provide
    async def get_protection_connector(self, config: ConnectorsConfig) -> AsyncIterator[ProtectionConnector]:
        protection = config.protection
        connector = ProtectionConnector(
            base_url=protection.base_url,
            timeout=protection.timeout,
            retry_count=protection.retry_count
        )
        yield connector
        await connector.close_connection()

class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_booking_service(
        self,
        db: DatabaseManager,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector,
    ) -> BookingService:
        return BookingService(db, payment_connector, protection_connector)

    @provide
    def get_event_service(self, db: DatabaseManager) -> EventService:
        return EventService(db)
    

class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_manager(self, config: RedisConfig) -> AsyncIterator[RedisManager]:
        redis = create_redis_manager(config)
        yield redis
        await redis.close()


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        DatabaseProvider(),
        RepositoryProvider(),
        ConnectorProvider(),
        ServiceProvider(),
        RedisProvider(),
    )