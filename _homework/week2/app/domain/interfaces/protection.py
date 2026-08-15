from typing import Protocol
from app.api.schemas.protection import ProtectionQuoteIn


class ProtectionPriceProcessor(Protocol):
    async def synchronize(self, payload: ProtectionQuoteIn) -> None: ...