from src.infrastructure.websocket.manager import WebsocketManager
from src.domain.events.event_payment_activity import EventPaymentActivity
from dataclasses import asdict


class WebsockerBroadcasterService:
    """Класс для отправки сообщений клиентам по вебсокету"""

    def __init__(self, ws_manager: WebsocketManager) -> None:
        self.ws_manager = ws_manager

    async def broadcast_aggregate_event_payment(self, events: list[EventPaymentActivity]) -> None:
        """Отправляет сообщение всем подключенным WebSocket клиентам"""
        await self.ws_manager.broadcast(
            {
                "items": [asdict(event) for event in events],
            }
        )
