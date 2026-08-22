from dishka import make_async_container, AsyncContainer
from app.config import Settings
from app.ioc import (
    ConfigProvider, DatabaseProvider, RepositoryProvider, 
    ConnectorProvider, ServiceProvider, RedisProvider, 
    QueueProvider, QueueProduceProvider, QueueConsumeProvider, 
    BackgroundProcessorProvider
)

def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        DatabaseProvider(),
        RepositoryProvider(),
        ConnectorProvider(),
        ServiceProvider(),
        RedisProvider(),
        QueueProvider(),
        QueueProduceProvider(),
        QueueConsumeProvider(),
        BackgroundProcessorProvider(),
    )