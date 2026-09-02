import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from venv import logger
from fastapi import WebSocket
from uuid import uuid4
from fastapi.websockets import WebSocket, WebSocketDisconnect

@dataclass(frozen=True, slots=True)
class WebsocketClient:
    ws: WebSocket
    queue: asyncio.Queue


class WebsocketManager:
    def __init__(self) -> None:
        self.clients: dict[str, WebsocketClient] = {}
        
    @asynccontextmanager
    async def connect(self, ws: WebSocket):
        await ws.accept()
        client_id = uuid4().hex
        client = WebsocketClient(
            ws=ws,
            queue=asyncio.Queue()
        )
        self.clients[client_id] = client
        
        try:
            yield client
        finally:
            self.clients.pop(client_id)
            
    async def broadcast(self, message: dict) -> None:
        for client in self.clients.values():
            await client.queue.put(message)
            
    async def send_messages_to_client(self, client: WebsocketClient) -> None:
        while True:
            message = await client.queue.get()
            
            try:
                await asyncio.wait_for(client.ws.send_json(message), timeout=2)
            except (WebSocketDisconnect, RuntimeError):
                logger.info("Client disconnected, stopping sender")
                break
            except TimeoutError:
                logger.warning("Timeout sending, dropping message")
                continue