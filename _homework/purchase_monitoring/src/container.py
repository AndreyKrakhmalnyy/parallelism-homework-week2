from dishka import make_async_container, AsyncContainer
from src.config import Settings
from src.ioc import *


def create_container(settings: Settings) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(settings),
        DatabaseProvider(),
        KafkaProvider(),
        EventConsumerProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        WebsocketProvider()
    )