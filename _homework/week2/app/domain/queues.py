import asyncio
from typing import NewType

EventViewQueue = NewType("EventViewQueue", asyncio.Queue)
