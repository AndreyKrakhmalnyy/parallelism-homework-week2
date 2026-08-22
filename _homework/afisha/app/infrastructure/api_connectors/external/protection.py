from app.api.schemas.protection import ProtectionQuoteIn, ProtectionQuoteOut
from app.infrastructure.api_connectors.base import BaseHTTPConnector


class ProtectionConnector(BaseHTTPConnector):
    async def calculate(self, payload: ProtectionQuoteIn) -> ProtectionQuoteOut:
        response = await self.request(
            "POST", 
            "/protection/calculate",
            json=payload.model_dump(mode="json"),
            retry=True
        )
        response.raise_for_status()
        return ProtectionQuoteOut.model_validate(response.json())
