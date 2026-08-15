from app.infrastructure.taskiq.tasks import sync_protection_price
from app.domain.interfaces.protection import ProtectionPriceProcessor
from app.api.schemas.protection import ProtectionQuoteIn


class ProtectionPriceTaskDispatcher(ProtectionPriceProcessor):
    async def synchronize(self, payload: ProtectionQuoteIn) -> None:
        await sync_protection_price.kiq(payload)