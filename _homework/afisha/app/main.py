import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.queues.consumers.event_view import EventViewQueueConsumer
from app.logging_config import configure_logging
from app.infrastructure.postgres.manager import DatabaseManager
from app.add_event_data import add_event_data_to_db
from app.config import Settings, settings
from app.container import create_container
from app.api.routes import main_router

from dishka.integrations.fastapi import setup_dishka

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.dishka_container

    async with container() as request_container:
        db_manager = await request_container.get(DatabaseManager)
        await add_event_data_to_db(db_manager)

    event_view_consumer = await container.get(EventViewQueueConsumer)
    event_view_consumer.start()

    yield

    await event_view_consumer.stop()
    await container.close()

def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="API Afisha",
        lifespan=lifespan,
        debug=False,
        swagger_ui_parameters={
            "displayRequestDuration": True,
        },
    )
    container = create_container(settings)
    setup_dishka(container=container, app=app)
    app.include_router(main_router)
    
    return app

configure_logging()
logger.info(
    "Afisha app configured: host=%s port=%s",
    settings.app.host,
    settings.app.port,
)
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run("main:app")