from dishka import FromDishka
from fastapi import APIRouter, WebSocket
from dishka.integrations.fastapi import inject

from src.infrastructure.websocket.manager import WebsocketManager


router = APIRouter(tags=["Вебсокет: Данные по покупках билетов"])

@router.websocket("/ws/payment_activities")
@inject
async def get_payment_activities(
    ws: WebSocket,
    ws_manager: FromDishka[WebsocketManager],
):
    async with ws_manager.connect(ws) as client:
        await ws_manager.send_messages_to_client(client)