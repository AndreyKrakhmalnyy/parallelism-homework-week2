from contextlib import asynccontextmanager
import logging
from dishka import AsyncContainer
from fastapi import FastAPI
import uvicorn
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.faststream import setup_dishka as setup_dishka_faststream
from src.config import settings
from src.logging_config import configure_logging
from src.container import create_container
from faststream.kafka import KafkaBroker
from src.infrastructure.kafka.consumers.purchase_ticket import PurchaseTicketConsumer

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    container: AsyncContainer = app.state.dishka_container
    logger.info("Purchase monitoring lifespan started")
    broker = await container.get(KafkaBroker)
    setup_dishka_faststream(container=container, broker=broker)
    await container.get(PurchaseTicketConsumer)
    yield
    await container.close()


def create_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(title="Аналитика перемещения курьеров", lifespan=lifespan)
    setup_dishka_fastapi(container=container, app=app)
    configure_logging()
    return app

container = create_container(settings)
app = create_app(container)


if __name__ == "__main__":
    uvicorn.run(
        "purchase_monitoring.src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        loop="uvloop",
    )
