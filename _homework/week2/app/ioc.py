from typing import AsyncIterator
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.infrastructure.api_connectors.external.payment import PaymentConnector
from app.infrastructure.postgres.repositories.seat import SeatRepository
from app.infrastructure.postgres.repositories.event import EventRepository
from app.config import (
    ConnectorsConfig,
    PostgresConfig, 
    Settings
)
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from app.infrastructure.postgres.manager import DatabaseManager
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
    
class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_db_manager(self) -> DatabaseManager:
        return DatabaseManager()

    @provide(scope=Scope.REQUEST)
    async def get_session(self, manager: DatabaseManager) -> AsyncIterator[AsyncSession]:
        async with manager.session() as session:
            yield session

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
    async def get_payment_connector(self, connectors_conf: ConnectorsConfig) -> AsyncIterator[PaymentConnector]:
        payment = connectors_conf.payment
        connector = PaymentConnector(
            base_url=payment.base_url,
            timeout=payment.timeout,
            retry=payment.retry
        )
        yield connector
        connector.close_connection()

    @provide
    async def get_protection_connector(self, connectors_conf: ConnectorsConfig) -> AsyncIterator[ProtectionConnector]:
        protection = connectors_conf.protection
        connector = ProtectionConnector(
            base_url=protection.base_url,
            timeout=protection.timeout,
            retry=protection.retry
        )
        yield connector
        connector.close_connection()

def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        DatabaseProvider(),
        RepositoryProvider(),
        ConnectorProvider()
    )