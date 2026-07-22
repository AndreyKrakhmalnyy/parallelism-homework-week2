import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.add_event_data import add_event_data_to_db
from app.config import Settings, settings
from app.ioc import create_container
from app.api.routes import main_router

from dishka.integrations.fastapi import setup_dishka


@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_event_data_to_db()
    yield

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

app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run("main:app")