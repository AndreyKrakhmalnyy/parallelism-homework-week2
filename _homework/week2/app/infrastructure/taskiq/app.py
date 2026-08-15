from app.config import settings
from app.container import create_container
from dishka.integrations.taskiq import setup_dishka

from app.infrastructure.taskiq.brokers import *
import app.infrastructure.taskiq.tasks

_taskiq_container = create_container(settings)

setup_dishka(container=_taskiq_container, broker=cpu_broker)
setup_dishka(container=_taskiq_container, broker=asyncio_broker)
